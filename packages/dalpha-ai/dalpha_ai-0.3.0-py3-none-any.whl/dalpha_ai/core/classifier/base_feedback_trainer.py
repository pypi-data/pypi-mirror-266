import inspect
import logging
import traceback
import timm
from typing import List

import pytorch_lightning as pl
import torch
import torch.nn as nn
from peft import LoraConfig, get_peft_model
from transformers import get_linear_schedule_with_warmup, AutoConfig

from .head_classifier import *
from .trainer_util import (
    TextClassifierInputPreprocess,
    TextClassifierSelectToken,
    ImageClassifierInputPreprocess,
    ModelEMA,
    find_indices_based_on_max_and_label,
)
from ..losses import (
    LOSSES,
    cross_entropy_from_probabilities,
    binary_cross_entropy_from_probabilities,
)
from torch.nn import functional as F

logger = logging.getLogger(__name__)

from PIL import Image

if hasattr(Image, "Resampling"):
    _pil_interpolation_to_str = {
        Image.Resampling.NEAREST: "nearest",
        Image.Resampling.BILINEAR: "bilinear",
        Image.Resampling.BICUBIC: "bicubic",
        Image.Resampling.BOX: "box",
        Image.Resampling.HAMMING: "hamming",
        Image.Resampling.LANCZOS: "lanczos",
    }
else:
    _pil_interpolation_to_str = {
        Image.NEAREST: "nearest",
        Image.BILINEAR: "bilinear",
        Image.BICUBIC: "bicubic",
        Image.BOX: "box",
        Image.HAMMING: "hamming",
        Image.LANCZOS: "lanczos",
    }


class TransformerWrapper(nn.Module):
    """
    Wrapper for transformers model to use in PyTorch Lightning (compatible with timm)
    """

    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        return self.model(pixel_values=x).pooler_output


class FeedbackBaseClassifierModule(pl.LightningModule):
    """
    Base class for all classifier modules

    Args:
        train_config (TrainConfig): train config
    """

    def __init__(self, train_config):
        super().__init__()

        self.train_config = train_config
        self.criterion = LOSSES[train_config.criterion]

        self.automatic_optimization = False
        self.train_step_outputs = []
        self.validation_step_outputs = []
        self.test_step_outputs = []
        self.test_result = []
        self.ema_backbone = None

    def on_train_epoch_start(self) -> None:
        from .image_text_classifier.image_text_config import ImageTextClassifierConfig

        if type(self.train_config) == ImageTextClassifierConfig:
            self.text_backbone.train()
            self.image_backbone.train()
            self.backbone_list = nn.ModuleList(
                [self.image_backbone, self.text_backbone]
            )
        else:
            self.backbone.train()
            self.backbone_list = nn.ModuleList([self.backbone])
        self.ema_backbone = ModelEMA(
            self.backbone_list, self.train_config.feedback_ema_decay
        )
        for ema_backbone in self.ema_backbone.ema:
            ema_backbone.eval()
        self.ema_backbone.updates = 0

        self.classifier_head.train()
        self.ema_classifier_head = ModelEMA(
            (self.classifier_head,), self.train_config.feedback_ema_decay
        )
        for ema_classifier in self.ema_classifier_head.ema:
            ema_classifier.eval()
        self.ema_classifier_head.updates = 0

    def get_model(self):
        raise NotImplementedError

    def forward(self):
        raise NotImplementedError

    def configure_optimizers(self):
        raise NotImplementedError

    ## Bugfixed in peft 0.7.0 (so we cast lora weights to float, for mixed precision training)
    def cast_lora_to_float(self, model: nn.Module):
        for name, mod in model.named_modules():
            if ("lora_" in name) and hasattr(mod, "weight"):
                mod.weight.data = mod.weight.data.float()
            if ("lora_" in name) and hasattr(mod, "bias") and (mod.bias is not None):
                mod.bias.data = mod.bias.data.float()
            if ("modules_to_save" in name) and isinstance(mod, nn.Linear):
                mod.weight.data = mod.weight.data.float()
                if mod.bias is not None:
                    mod.bias.data = mod.bias.data.float()

    def load_model(
        self,
        model: nn.Module,
        freeze: bool,
        lora: bool,
        lora_r: float,
        lora_alpha: float,
        lora_target_modules: List[str],
        lora_dropout: float,
    ):
        """
        Load model and set up LORA if necessary

        Args:
            model (nn.Module): model
            freeze (bool): whether to freeze the backbone
            lora (bool): whether to use LORA
            lora_r (float): LORA r parameter
            lora_alpha (float): LORA alpha parameter
            lora_target_modules (list with string): LORA target modules
            lora_dropout (float): LORA dropout parameter
        """
        # Freeze
        if freeze:
            logger.info("Fine-tuning while backbone freezed.")
            for param in model.parameters():
                param.requires_grad = False
            model.eval()
        # LORA finetuning
        elif lora:
            logger.info("Fine-tuning with LORA")
            lora_config = LoraConfig(
                r=lora_r,
                lora_alpha=lora_alpha,
                target_modules=lora_target_modules,
                lora_dropout=lora_dropout,
                modules_to_save=["classifier"],
            )
            try:
                model = get_peft_model(model, lora_config)
                self.cast_lora_to_float(model)
            except ValueError:
                raise ValueError(
                    f"Error message: {traceback.format_exc()}\n\nLORA failed, this may be due to the mismatch between lora_target_modules={lora_target_modules} and text model structure.\nThe structure of the text model is:\n{model}"
                )
        # Full fine-tuning
        else:
            logger.warning(
                "You are trying to train model without freezing the backbone or using LORA. You can encounter out of memory error easily."
            )

        return model

    def get_text_model(
        self,
        backbone_name: str,
        freeze: bool,
        lora: bool,
        lora_r: float,
        lora_alpha: float,
        lora_target_modules: List[str],
        lora_dropout: float,
    ):
        """
        Load text model and tokenizer

        Args:
            backbone_name (str): backbone name
            freeze (bool): whether to freeze the backbone
            lora (bool): whether to use LORA
            lora_r (float): LORA r parameter
            lora_alpha (float): LORA alpha parameter
            lora_target_modules (list with string): LORA target modules
            lora_dropout (float): LORA dropout parameter

        """
        from transformers import AutoConfig, AutoModel, AutoTokenizer

        logger.info("Loading pretrained model...")
        model = AutoModel.from_pretrained(
            backbone_name, low_cpu_mem_usage=True, torch_dtype="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(backbone_name)
        config = AutoConfig.from_pretrained(backbone_name)
        # # Save initial config for future use.
        # self.initial_config = config
        # self.embedding_size = config.hidden_size

        # Check unnecssary input keys
        forward_parameters = inspect.signature(model.forward).parameters
        delete_input_key_list = []
        for input_key in tokenizer.model_input_names:
            if input_key not in forward_parameters.keys():
                delete_input_key_list.append(input_key)
                logger.info(
                    f"{input_key} not needed for model forward, will be deleted automatically."
                )
        model = self.load_model(
            model, freeze, lora, lora_r, lora_alpha, lora_target_modules, lora_dropout
        )

        return model, tokenizer, config, delete_input_key_list

    def get_image_model(
        self,
        backbone_name: str,
        freeze: bool,
        lora: bool,
        lora_r: float,
        lora_alpha: float,
        lora_target_modules: List[str],
        lora_dropout: float,
    ):
        """
        Load image model

        Args:
            backbone_name (str): backbone name
            freeze (bool): whether to freeze the backbone
            lora (bool): whether to use LORA
            lora_r (float): LORA r parameter
            lora_alpha (float): LORA alpha parameter
            lora_target_modules (list with string): LORA target modules
            lora_dropout (float): LORA dropout parameter
        """
        if backbone_name in timm.list_models(pretrained=True):
            model = timm.create_model(
                backbone_name, pretrained=True, num_classes=0
            )  # remove linear classifier

            data_config = timm.data.resolve_model_data_config(model)
            train_transforms = timm.data.create_transform(
                **data_config, is_training=True
            )
            val_transforms = timm.data.create_transform(
                **data_config, is_training=False
            )
            data_config["scale"] = (self.train_config.crop_ratio, 1.0)
            timm_flag = True
            config = None
            # self.train_config.timm = True
        else:
            timm_flag = False

            from transformers import (
                AutoImageProcessor,
                AutoModel,
                CLIPModel,
                AutoConfig,
            )

            model = AutoModel.from_pretrained(backbone_name)
            if isinstance(model, CLIPModel):
                model = model.vision_model
                # Cannot converted with huggingface
                timm_flag = True
            model = TransformerWrapper(model)
            image_processor = AutoImageProcessor.from_pretrained(backbone_name)
            config = AutoConfig.from_pretrained(backbone_name)

            if hasattr(image_processor, "crop_size"):
                data_config = {
                    "input_size": (
                        3,
                        image_processor.crop_size["height"],
                        image_processor.crop_size["width"],
                    ),
                    "mean": image_processor.image_mean,
                    "std": image_processor.image_std,
                    "interpolation": _pil_interpolation_to_str[
                        image_processor.resample
                    ],
                    "scale": (self.train_config.crop_ratio, 1.0),
                }
            elif hasattr(image_processor, "size"):
                data_config = {
                    "input_size": (
                        3,
                        image_processor.size["height"],
                        image_processor.size["width"],
                    ),
                    "mean": image_processor.image_mean,
                    "std": image_processor.image_std,
                    "interpolation": _pil_interpolation_to_str[
                        image_processor.resample
                    ],
                    "scale": (self.train_config.crop_ratio, 1.0),
                }
            else:
                raise ValueError(
                    f"'size' and 'crop_size' does not exist in current Image processor. Current image processor: {image_processor}"
                )

            train_transforms = timm.data.create_transform(
                **data_config,
                auto_augment=self.train_config.auto_augment,
                is_training=True,
            )
            val_transforms = timm.data.create_transform(
                **data_config, is_training=False
            )

        model = self.load_model(
            model, freeze, lora, lora_r, lora_alpha, lora_target_modules, lora_dropout
        )

        return model, train_transforms, val_transforms, data_config, timm_flag, config

    def text_forward(
        self,
        input_texts: List[str],
        backbone: nn.Module,
        classifier_head: nn.Module,
        initial_config: AutoConfig,
        freeze: bool = False,
        eval: bool = False,
        classifier: bool = True,
    ):
        """
        Forward function for text model

        Args:
            input_texts (List[str]): list of input texts
            backbone (nn.Module): backbone model
            eval (bool): whether to use eval mode
            freeze (bool): whether to freeze the backbone
            classifier (bool): whether to use classifier head
            initial_config (AutoConfig): initial config
        """
        inputs = TextClassifierInputPreprocess(
            input_texts,
            text_prompt=self.train_config.text_prompt,
            device=self.device,
            tokenizer=self.tokenizer,
        )

        # Delete unnecessary input keys
        for delete_input_key in self.delete_input_key_list:
            del inputs[delete_input_key]

        # For classificaiton, model use the last token as other causal models (e.g. GPT-1) do. We utilize attention mask to know the position of the last token.
        if eval:
            with torch.no_grad():
                backbone_outputs = backbone(**inputs)
                backbone_outputs = TextClassifierSelectToken(
                    backbone_outputs, inputs=inputs, configs=initial_config
                )
                if not classifier:
                    return backbone_outputs
                logits = classifier_head(backbone_outputs)
            return logits
        else:
            if freeze:
                # Do not compute gradient for backbone weights
                with torch.no_grad():
                    backbone_outputs = backbone(**inputs)
                    backbone_outputs = TextClassifierSelectToken(
                        backbone_outputs, inputs=inputs, configs=initial_config
                    )
            # LORA and full fine-tuning case.
            else:
                backbone_outputs = backbone(**inputs)
                backbone_outputs = TextClassifierSelectToken(
                    backbone_outputs, inputs=inputs, configs=initial_config
                )

            if not classifier:
                return backbone_outputs
            logits = classifier_head(backbone_outputs)

            return logits

    def image_forward(
        self,
        input_img_paths: List[str],
        backbone: nn.Module,
        classifier_head: nn.Module,
        freeze: bool = False,
        eval: bool = False,
        classifier: bool = True,
    ):
        """
        Forward function for image model

        Args:
            input_img_paths (List[str]): input image paths
            backbone (nn.Module): backbone model
            eval (bool): whether to use eval mode
            freeze (bool): whether to freeze the backbone
            classifier (bool): whether to use classifier head
        """
        if eval:
            inputs = ImageClassifierInputPreprocess(
                input_img_paths,
                device=self.device,
                transforms=self.val_transforms,
            )
            with torch.no_grad():
                backbone_outputs = backbone.forward(inputs)
                if not classifier:
                    return backbone_outputs
                logits = classifier_head(backbone_outputs)
            return logits
        else:
            inputs = ImageClassifierInputPreprocess(
                input_img_paths,
                device=self.device,
                transforms=self.train_transforms,
            )
            if freeze:
                # Do not compute gradient for backbone weights
                with torch.no_grad():
                    backbone_outputs = backbone.forward(inputs)
            # LORA and full fine-tuning case.
            else:
                backbone_outputs = backbone.forward(inputs)

            if not classifier:
                return backbone_outputs

            logits = classifier_head(backbone_outputs)

            return logits

    def training_step(self, batch, batch_idx: int):
        """
        Training step for LightningModule
        """

        self.ema_backbone.update(self.backbone_list)

        self.ema_classifier_head.update((self.classifier_head,))
        feedback_flags = batch[-1]
        labels = batch[-2]
        inputs = batch[:-2]
        if self.train_config.problem_type == "single_label_classification":
            labels = labels.type(torch.int64)
        logits = self.forward(*inputs)
        feedback_idx = [
            index for index, value in enumerate(feedback_flags) if value == 1
        ]
        non_feedback_idx = [
            index for index, value in enumerate(feedback_flags) if value == 0
        ]
        non_feedback_inputs = [
            [sub_inputs[i] for i in non_feedback_idx] for sub_inputs in inputs
        ]
        feedback_inputs = [
            [sub_inputs[i] for i in feedback_idx] for sub_inputs in inputs
        ]
        # For feedback data, we use self-play finetuning loss. https://arxiv.org/pdf/2401.01335.pdf (Zixiang Chen)
        if feedback_idx:
            if self.train_config.problem_type == "single_label_classification":
                feedback_logits = logits[feedback_idx]
                feedback_labels = labels[feedback_idx]
                feedback_prob = F.softmax(feedback_logits / 1.0, dim=1)
                true_prob = feedback_prob[
                    torch.arange(len(feedback_labels)), feedback_labels
                ]
                pred_prob = torch.max(feedback_prob, dim=1).values

                pseudo_feedback_logits = self.forward(
                    *feedback_inputs,
                    *self.ema_backbone.ema,
                    *self.ema_classifier_head.ema,
                    eval=True,
                )
                pseudo_feedback_prob = F.softmax(pseudo_feedback_logits / 1.0, dim=1)
                pseudo_true_prob = pseudo_feedback_prob[
                    torch.arange(len(feedback_labels)), feedback_labels
                ]
                pseudo_pred_prob = torch.max(pseudo_feedback_prob, dim=1).values

                # feedback_loss = torch.log(1 + torch.exp(-(torch.log(true_prob / pseudo_true_prob) - torch.log(pred_prob / pseudo_pred_prob))))
                feedback_loss = torch.log(
                    1
                    + torch.exp(
                        -(
                            torch.log(true_prob / (pseudo_true_prob + 1e-9) + 1e-9)
                            - torch.log(pred_prob / (pseudo_pred_prob + 1e-9) + 1e-9)
                        )
                    )
                )
                feedback_loss = torch.sum(feedback_loss)
            else:
                feedback_logits = logits[feedback_idx]
                feedback_labels = labels[feedback_idx]
                feedback_prob = F.sigmoid(feedback_logits)
                true_prob = (1 - feedback_labels) * (
                    1 - feedback_prob
                ) + feedback_labels * feedback_prob
                pred_prob = torch.abs(feedback_prob - 0.5) + 0.5

                pseudo_feedback_logits = self.forward(
                    *feedback_inputs,
                    *self.ema_backbone.ema,
                    *self.ema_classifier_head.ema,
                    eval=True,
                )
                pseudo_feedback_prob = F.sigmoid(pseudo_feedback_logits)
                pseudo_true_prob = (1 - feedback_labels) * (
                    1 - pseudo_feedback_prob
                ) + feedback_labels * pseudo_feedback_prob
                pseudo_pred_prob = torch.abs(pseudo_feedback_prob - 0.5) + 0.5

                feedback_loss = torch.log(
                    1
                    + torch.exp(
                        -(
                            torch.log(true_prob / (pseudo_true_prob + 1e-9) + 1e-9)
                            - torch.log(pred_prob / (pseudo_pred_prob + 1e-9) + 1e-9)
                        )
                    )
                )
                feedback_loss = torch.sum(feedback_loss)

                # feedback_loss = self.criterion(feedback_logits, feedback_labels, label_smoothing=self.train_config.label_smoothing_factor, reduction="sum")
        else:
            feedback_loss = 0

        # For non-feedback data(=sample from trai data), we use cross entropy loss(or focal loss, depend on user-defined criterion) & Knowledge distillation loss. only use cross entropy loss
        # for high confidence samples (e.g. softmax > 0.7) and same predictions and labels.
        if non_feedback_idx:
            if self.train_config.problem_type == "single_label_classification":
                non_feedback_logits = logits[non_feedback_idx]
                softmax_non_feedback_logits = F.softmax(
                    non_feedback_logits / 1.0, dim=1
                )

                higher_idx, lower_idx = find_indices_based_on_max_and_label(
                    softmax_non_feedback_logits, labels[non_feedback_idx], threshold=0.7
                )

                higher_cross_entropy_loss = self.criterion(
                    non_feedback_logits[higher_idx],
                    labels[non_feedback_idx][higher_idx],
                    label_smoothing=self.train_config.label_smoothing_factor,
                    reduction="sum",
                )

                lower_non_feedback_inputs = [
                    [sub_inputs[i] for i in lower_idx]
                    for sub_inputs in non_feedback_inputs
                ]
                if len(lower_idx) > 0:
                    non_feedback_logits = self.forward(
                        *lower_non_feedback_inputs,
                        *self.ema_backbone.ema,
                        *self.ema_classifier_head.ema,
                        eval=True,
                    )

                    softmax_pseudo_label_logit = F.softmax(
                        non_feedback_logits / 1.0, dim=1
                    )

                    # Knowledge distillation losss
                    lower_kd_loss = cross_entropy_from_probabilities(
                        softmax_pseudo_label_logit,
                        softmax_non_feedback_logits[lower_idx],
                    )

                else:
                    lower_kd_loss = 0

            else:  # multi-label classification
                non_feedback_logits = logits[non_feedback_idx]
                non_feedback_labels = labels[non_feedback_idx]
                non_feedback_prob = F.sigmoid(non_feedback_logits)

                # flattening for simple calculation
                non_feedback_prob = non_feedback_prob.view(-1)
                non_feedback_labels = non_feedback_labels.view(-1)

                higher_idx = torch.where(
                    torch.abs(non_feedback_prob - non_feedback_labels) <= 0.1
                )[0]
                lower_idx = torch.where(
                    torch.abs(non_feedback_prob - non_feedback_labels) > 0.1
                )[0]

                higher_cross_entropy_loss = self.criterion(
                    non_feedback_logits.view(-1)[higher_idx],
                    non_feedback_labels[higher_idx],
                    label_smoothing=self.train_config.label_smoothing_factor,
                    reduction="sum",
                )

                if len(lower_idx) > 0:
                    non_feedback_pseudo_logits = self.forward(
                        *non_feedback_inputs,
                        *self.ema_backbone.ema,
                        *self.ema_classifier_head.ema,
                        eval=True,
                    )
                    pseudo_non_feedback_prob = F.sigmoid(non_feedback_pseudo_logits)
                    pseudo_non_feedback_prob = pseudo_non_feedback_prob.view(-1)

                    lower_kd_loss = binary_cross_entropy_from_probabilities(
                        pseudo_non_feedback_prob[lower_idx],
                        non_feedback_prob[lower_idx],
                    )

                else:
                    lower_kd_loss = 0

            non_feedback_loss = lower_kd_loss + higher_cross_entropy_loss

        else:
            non_feedback_loss = 0

        loss = (feedback_loss + non_feedback_loss) / len(labels)
        ## loss가 nan인지 확인
        if torch.isnan(loss):
            breakpoint()

        self.log("train/loss", loss.item(), prog_bar=True)

        # Manual backward
        opt = self.optimizers()
        sch = self.lr_schedulers()
        sch.step()
        self.manual_backward(loss)

        if self.train_config.gradient_accumulation_steps > 1:
            # Apply gradient accumulation
            if (batch_idx + 1) % self.train_config.gradient_accumulation_step == 0:
                opt.step()
                opt.zero_grad()
        else:
            opt.step()
            opt.zero_grad()

        if self.train_config.problem_type == "single_label_classification":
            _, prediction = torch.max(logits, 1)
            correct_pred = (prediction == labels).sum().item()
            total_pred = len(prediction)
            self.train_step_outputs.append(
                {"correct_pred": correct_pred, "total_pred": total_pred}
            )

        else:
            preds = torch.where(
                logits > 0, torch.ones_like(logits), torch.zeros_like(logits)
            )
            TP = (preds * labels).sum(dim=0)
            FP = (preds * (1 - labels)).sum(dim=0)
            FN = ((1 - preds) * labels).sum(dim=0)
            TN = ((1 - preds) * (1 - labels)).sum(dim=0)

            self.train_step_outputs.append({"TP": TP, "FP": FP, "FN": FN, "TN": TN})

    @torch.no_grad()
    def validation_step(self, batch, batch_idx: int):
        """
        Validation step for LightningModule
        """
        labels = batch[-1]
        inputs = batch[:-1]
        # input_img_paths, labels = batch
        if self.train_config.problem_type == "single_label_classification":
            labels = labels.type(torch.int64)

        if self.ema_backbone is None:
            logits = self.forward(*inputs, eval=True)
        else:
            logits = self.forward(
                *inputs,
                *self.ema_backbone.ema,
                *self.ema_classifier_head.ema,
                eval=True,
            )

        val_loss = self.criterion(
            logits, labels, label_smoothing=self.train_config.label_smoothing_factor
        )
        self.log("val/loss", val_loss.item(), prog_bar=True)

        if self.train_config.problem_type == "single_label_classification":
            # Calculate for topk accuracy
            topk_list = self.train_config.print_topk_list
            correct_pred_list = []
            for topk in topk_list:
                _, predictions = logits.topk(topk, 1, True, True)
                correct_pred = predictions.eq(labels.view(-1, 1)).view(-1).sum().item()
                correct_pred_list.append(correct_pred)

            total_pred = len(predictions)

            self.validation_step_outputs.append(
                {"correct_pred_list": correct_pred_list, "total_pred": total_pred}
            )
        # Multi-label classification
        else:
            preds = torch.where(
                logits > 0, torch.ones_like(logits), torch.zeros_like(logits)
            )
            TP = (preds * labels).sum(dim=0)
            FP = (preds * (1 - labels)).sum(dim=0)
            FN = ((1 - preds) * labels).sum(dim=0)
            TN = ((1 - preds) * (1 - labels)).sum(dim=0)

            self.validation_step_outputs.append(
                {"TP": TP, "FP": FP, "FN": FN, "TN": TN}
            )

    def test_step(self, batch, batch_idx: int):
        """
        Test step for LightningModule
        """
        labels = batch[-1]
        inputs = batch[:-1]
        # input_img_paths, labels = batch
        if self.train_config.problem_type == "single_label_classification":
            labels = labels.type(torch.int64)

        if self.ema_backbone is None:
            logits = self.forward(*inputs, eval=True)
        else:
            logits = self.forward(
                *inputs,
                *self.ema_backbone.ema,
                *self.ema_classifier_head.ema,
                eval=True,
            )

        # val_loss = F.cross_entropy(
        #     logits, labels, label_smoothing=self.train_config.label_smoothing_factor
        # )
        test_loss = self.criterion(
            logits, labels, label_smoothing=self.train_config.label_smoothing_factor
        )
        self.log("test/loss", test_loss.item(), prog_bar=True, sync_dist=True)
        if self.train_config.problem_type == "single_label_classification":
            # Calculate for topk accuracy
            topk_list = self.train_config.print_topk_list
            correct_pred_list = []
            for topk in topk_list:
                _, predictions = logits.topk(topk, 1, True, True)
                correct_pred = predictions.eq(labels.view(-1, 1)).view(-1).sum().item()
                correct_pred_list.append(correct_pred)

            total_pred = len(predictions)

            self.test_step_outputs.append(
                {"correct_pred_list": correct_pred_list, "total_pred": total_pred}
            )
        # Multi-label classification
        else:
            preds = torch.where(
                logits > 0, torch.ones_like(logits), torch.zeros_like(logits)
            )
            TP = (preds * labels).sum(dim=0)
            FP = (preds * (1 - labels)).sum(dim=0)
            FN = ((1 - preds) * labels).sum(dim=0)
            TN = ((1 - preds) * (1 - labels)).sum(dim=0)

            self.test_step_outputs.append({"TP": TP, "FP": FP, "FN": FN, "TN": TN})

    def on_train_epoch_end(self):
        """
        Called at the end of training epoch, here we log the train accuracy or other metrics e.g. f1 score
        """
        # self.ema_backbone.update_attr(self.backbone)
        # self.ema_classifier_head.update_attr(self.classifier_head)
        # self.backbone = self.ema_backbone.ema
        # self.classifier_head = self.ema_classifier_head.ema
        if self.train_config.problem_type == "single_label_classification":
            total_correct_pred = sum(
                list(map(lambda x: x["correct_pred"], self.train_step_outputs))
            )
            total_pred_count = sum(
                list(map(lambda x: x["total_pred"], self.train_step_outputs))
            )
            train_acc = total_correct_pred / total_pred_count
            # For multi gpu training
            train_acc = self.all_gather(train_acc).mean().item()
            self.log("train/acc", train_acc, sync_dist=True)
            if self.global_rank == 0:
                print(f"\ntrain accuracy {train_acc} at epoch {self.current_epoch}")
            self.train_step_outputs.clear()

        # Multi-label classification
        else:
            TP = torch.sum(
                torch.stack(list(map(lambda x: x["TP"], self.train_step_outputs)))
            )
            FP = torch.sum(
                torch.stack(list(map(lambda x: x["FP"], self.train_step_outputs)))
            )
            FN = torch.sum(
                torch.stack(list(map(lambda x: x["FN"], self.train_step_outputs)))
            )
            TN = torch.sum(
                torch.stack(list(map(lambda x: x["TN"], self.train_step_outputs)))
            )

            train_precision = torch.nanmean(TP / (TP + FP))
            train_recall = torch.nanmean(TP / (TP + FN))
            train_f1 = (
                2 * train_precision * train_recall / (train_precision + train_recall)
            )
            # For multi gpu training
            train_precision = self.all_gather(train_precision).mean().item()
            train_recall = self.all_gather(train_recall).mean().item()
            train_f1 = self.all_gather(train_f1).mean().item()

            self.log("train/precision", train_precision, sync_dist=True)
            self.log("train/recall", train_recall, sync_dist=True)
            self.log("train/f1", train_f1, sync_dist=True)

            if self.global_rank == 0:
                print(
                    f"\ntrain precision {train_precision} at epoch {self.current_epoch}"
                )
                print(f"\ntrain recall {train_recall} at epoch {self.current_epoch}")
                print(f"\ntrain f1 {train_f1} at epoch {self.current_epoch}")

            self.train_step_outputs.clear()

        # if type(self.train_config) == ImageTextClassifierConfig:
        #     self.text_backbone.train()
        #     self.image_backbone.train()
        #     self.backbone_list = nn.ModuleList([self.image_backbone, self.text_backbone])
        # else:
        #     self.backbone.train()
        #     self.backbone_list = nn.ModuleList([self.backbone])
        # self.ema_backbone = ModelEMA(self.backbone_list, self.train_config.feedback_ema_decay)
        # for ema_backbone in self.ema_backbone.ema:
        #     ema_backbone.eval()
        # self.ema_backbone.updates = 0

        # self.classifier_head.train()
        # self.ema_classifier_head = ModelEMA((self.classifier_head, ), self.train_config.feedback_ema_decay)

        # from .image_text_classifier.image_text_config import ImageTextClassifierConfig

        self.ema_backbone.update_attr(self.backbone_list, self.ema_backbone.ema)
        self.ema_classifier_head.update_attr(
            (self.classifier_head,), self.ema_classifier_head.ema
        )

        # if type(self.train_config) == ImageTextClassifierConfig:
        #     self.ema_backbone.update_attr(self.image_backbone, self.ema_backbone.ema[0])
        #     self.ema_backbone.update_attr(self.text_backbone, self.ema_backbone.ema[1])
        #     self.image_backbone, self.text_backbone = self.ema_backbone.ema
        # else:
        #     self.backbone = self.ema_backbone.ema[0]
        # self.classifier_head = self.ema_classifier_head.ema[0]
        del self.ema_backbone
        del self.ema_classifier_head
        del self.backbone_list
        self.ema_backbone = None
        self.ema_classifier_head = None

    def on_validation_epoch_end(self):
        """
        Called at the end of validation epoch, here we log the validation accuracy or other metrics e.g. f1 score
        """
        if self.train_config.problem_type == "single_label_classification":
            # Print top k accuracy
            total_correct_pred_list = list(
                map(lambda x: x["correct_pred_list"], self.validation_step_outputs)
            )

            topk_correct_count_list = []
            for topk_idx in range(len(total_correct_pred_list[0])):
                topk_correct_count_list.append(
                    sum(list(map(lambda x: x[topk_idx], total_correct_pred_list)))
                )

            total_pred_count = sum(
                list(map(lambda x: x["total_pred"], self.validation_step_outputs))
            )

            topk_val_acc_list = []
            for topk_correct_count in topk_correct_count_list:
                topk_val_acc = topk_correct_count / total_pred_count
                # For multi gpu training
                topk_val_acc = self.all_gather(topk_val_acc).mean().item()
                topk_val_acc_list.append(topk_val_acc)

            for topk_val_acc, topk in zip(
                topk_val_acc_list, self.train_config.print_topk_list
            ):
                if self.global_rank == 0:
                    print(
                        f"\nTop {topk} Validation accuracy {topk_val_acc} at epoch {self.current_epoch}"
                    )
                self.log(f"val/acc{topk}", topk_val_acc, sync_dist=True)

            # Monitoring accuracy, used in naming checkpoint file.
            if self.train_config.monitor_topk != "total":
                monitor_topk_index = self.train_config.print_topk_list.index(
                    self.train_config.monitor_topk
                )
                self.log(
                    "val/monitor_acc",
                    topk_val_acc_list[monitor_topk_index],
                    sync_dist=True,
                )
            else:
                self.log("val/monitor_acc", sum(topk_val_acc_list), sync_dist=True)

            # Total sum accuracy
            self.log("val/tot_acc", sum(topk_val_acc_list), sync_dist=True)
            self.validation_step_outputs.clear()
        # Multi-label classification
        else:
            TP = torch.sum(
                torch.stack(list(map(lambda x: x["TP"], self.validation_step_outputs)))
            )
            FP = torch.sum(
                torch.stack(list(map(lambda x: x["FP"], self.validation_step_outputs)))
            )
            FN = torch.sum(
                torch.stack(list(map(lambda x: x["FN"], self.validation_step_outputs)))
            )
            TN = torch.sum(
                torch.stack(list(map(lambda x: x["TN"], self.validation_step_outputs)))
            )

            val_precision = torch.nanmean(TP / (TP + FP))
            val_recall = torch.nanmean(TP / (TP + FN))
            val_f1 = 2 * val_precision * val_recall / (val_precision + val_recall)
            # For multi gpu training
            val_precision = self.all_gather(val_precision).mean().item()
            val_recall = self.all_gather(val_recall).mean().item()
            val_f1 = self.all_gather(val_f1).mean().item()

            self.log("val/precision", val_precision, sync_dist=True)
            self.log("val/recall", val_recall, sync_dist=True)
            self.log("val/f1", val_f1, sync_dist=True)

            if self.global_rank == 0:
                print(f"\nval precision {val_precision} at epoch {self.current_epoch}")
                print(f"\nval recall {val_recall} at epoch {self.current_epoch}")
                print(f"\nval f1 {val_f1} at epoch {self.current_epoch}")

            self.validation_step_outputs.clear()

    def on_test_epoch_end(self):
        """
        Called at the end of test epoch, here we log the test accuracy or other metrics e.g. f1 score
        """
        if self.train_config.problem_type == "single_label_classification":
            # Print top k accuracy
            total_correct_pred_list = list(
                map(lambda x: x["correct_pred_list"], self.test_step_outputs)
            )

            topk_correct_count_list = []
            for topk_idx in range(len(total_correct_pred_list[0])):
                topk_correct_count_list.append(
                    sum(list(map(lambda x: x[topk_idx], total_correct_pred_list)))
                )

            total_pred_count = sum(
                list(map(lambda x: x["total_pred"], self.test_step_outputs))
            )

            topk_test_acc_list = []
            for topk_correct_count in topk_correct_count_list:
                topk_test_acc = topk_correct_count / total_pred_count
                # For multi gpu training
                topk_test_acc = self.all_gather(topk_test_acc).mean().item()
                topk_test_acc_list.append(topk_test_acc)

            for topk_test_acc, topk in zip(
                topk_test_acc_list, self.train_config.print_topk_list
            ):
                if self.global_rank == 0:
                    print(
                        f"\nTop {topk} Test accuracy {topk_test_acc} at epoch {self.current_epoch}"
                    )
                self.log(f"test/acc{topk}", topk_test_acc, sync_dist=True)

            # Total sum accuracy
            self.log("test/tot_acc", sum(topk_test_acc_list), sync_dist=True)
            self.test_step_outputs.clear()
        # Multi-label classification
        else:
            TP = torch.sum(
                torch.stack(list(map(lambda x: x["TP"], self.test_step_outputs)))
            )
            FP = torch.sum(
                torch.stack(list(map(lambda x: x["FP"], self.test_step_outputs)))
            )
            FN = torch.sum(
                torch.stack(list(map(lambda x: x["FN"], self.test_step_outputs)))
            )
            TN = torch.sum(
                torch.stack(list(map(lambda x: x["TN"], self.test_step_outputs)))
            )

            test_precision = torch.nanmean(TP / (TP + FP))
            test_recall = torch.nanmean(TP / (TP + FN))
            test_f1 = 2 * test_precision * test_recall / (test_precision + test_recall)
            # For multi gpu training
            test_precision = self.all_gather(test_precision).mean().item()
            test_recall = self.all_gather(test_recall).mean().item()
            test_f1 = self.all_gather(test_f1).mean().item()

            self.log("test/precision", test_precision, sync_dist=True)
            self.log("test/recall", test_recall, sync_dist=True)
            self.log("test/f1", test_f1, sync_dist=True)

            if self.global_rank == 0:
                print(
                    f"\ntest precision {test_precision} at epoch {self.current_epoch}"
                )
                print(f"\ntest recall {test_recall} at epoch {self.current_epoch}")
                print(f"\ntest f1 {test_f1} at epoch {self.current_epoch}")

            self.test_step_outputs.clear()

    def classifier_head_optimizers(self):
        """
        Returns the optimizer for the classifier head
        """
        return torch.optim.AdamW(
            self.classifier_head.parameters(),
            lr=self.train_config.classifier_learning_rate,
        )

    # Text Optimizer setup
    def add_optimizers(
        self,
        optimizer: torch.optim.Optimizer,
        backbone: nn.Module,
        freeze: bool,
        lora: bool,
        backbone_learning_rate: float,
    ):
        """
        Adds the optimizer for the backbone
        """
        # Classifier head fine-tuning
        if freeze:
            return optimizer
        # LORA fine-tuning
        elif lora:
            lora_pg = []
            for name, params in backbone.named_parameters():
                if "lora" in name:
                    lora_pg.append(params)
            optimizer.add_param_group({"params": lora_pg, "lr": backbone_learning_rate})
        # Full fine-tuning
        else:
            backbone_pg = []
            for name, params in backbone.named_parameters():
                backbone_pg.append(params)
            optimizer.add_param_group(
                {"params": backbone_pg, "lr": backbone_learning_rate}
            )
        return optimizer

    def get_lr_scheduler(self, optimizer, lr_scheduler_type: str):
        """
        Get the learning rate scheduler (Currently supporting only linear warmup, will be adding more in future)
        """
        if lr_scheduler_type == "linear_warmup":
            lr_scheduler = get_linear_schedule_with_warmup(
                optimizer=optimizer,
                num_warmup_steps=0.06 * self.trainer.estimated_stepping_batches,
                num_training_steps=self.trainer.estimated_stepping_batches,
            )
        elif lr_scheduler_type == "constant":
            lambda_constant = lambda epoch: 1.0
            lr_scheduler = torch.optim.lr_scheduler.LambdaLR(
                optimizer, lr_lambda=lambda_constant
            )
        else:
            raise ValueError(f"lr_scheduler_type {lr_scheduler_type} is not supported.")

        return lr_scheduler

    # def on_train_end(self):
    #     """
    #     Called at the end of training
    #     """
    #     from .image_text_classifier.image_text_config import ImageTextClassifierConfig
    #     if type(self.train_config) == ImageTextClassifierConfig:
    #         self.image_backbone, self.text_backbone = self.ema_backbone.ema
    #     else:
    #         self.backbone = self.ema_backbone.ema[0]
    #     self.classifier_head = self.ema_classifier_head.ema[0]
    #     del self.ema_backbone
    #     del self.ema_classifier_head
    #     self.ema_backbone = None
    #     self.ema_classifier_head = None
    #     breakpoint()
