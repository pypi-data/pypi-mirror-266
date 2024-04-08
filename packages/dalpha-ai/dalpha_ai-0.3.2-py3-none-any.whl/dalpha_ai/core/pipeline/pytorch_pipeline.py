import torch
import os
from ..classifier import *
from typing import Union, List
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

from .util import postprocess


class PytorchClassificationPipeline:
    """
    Pytorch Classification Pipeline

    Args:
        model_type (str): Model type, support TextClassifier, ImageClassifier, ImageTextClassifier.
        save_dir (str): Model directory.
        device (str, optional): Device for inference, support cpu and gpu. Defaults to "gpu".
    """

    def __init__(
        self,
        model_type: str,
        save_dir: str,
        device: str = "gpu",
        quantization: bool = False,
        optimization: bool = False,
    ):
        # Device setting
        if device == "cpu":
            self.device = torch.device("cpu")
            self.autocast_device = "cpu"
        elif device == "gpu":
            self.device = torch.device("cuda")
            self.autocast_device = "cuda"
        else:
            raise ValueError(
                f"Not supported device type: {device}, choose in ['cpu', 'gpu']."
            )
        self.model_type = model_type
        # Use pytorch lightning module for inferene pipeline.
        if model_type.endswith("Module"):
            train_module_name = model_type
        else:
            train_module_name = model_type + "Module"
        # Call model class with model type string
        if train_module_name not in globals().keys():
            raise ValueError(f"Not supported model type: {model_type}")

        # Load pretrained model
        model_class = globals()[train_module_name]
        ckpt_path = os.path.join(save_dir, "model.ckpt")
        self.pretrained_model = model_class.load_from_checkpoint(
            ckpt_path, map_location=self.device
        )
        self.pretrained_model.eval()

        self.label_name_list = self.pretrained_model.train_config.label_name_list

    def __call__(
        self,
        inputs: Union[str, List[str]],
        topk: int = 1,
        return_logits: bool = False,
        sigmoid: bool = False,
        only_backbone: bool = False,
        last_embedding: bool = False,
        temperature: float = 1.0,
    ):
        """
        Args:
            inputs (Union[str, List[str]]): Input text or list of input texts.
            topk (int, optional): Top k prediction. Defaults to 1.
            return_logits (bool, optional): Return logits or not. Defaults to False.
            sigmoid (bool, optional): Apply sigmoid to logits or not. Defaults to False.
        """
        if only_backbone and last_embedding:
            raise ValueError(
                "only_backbone and last_embedding cannot be True at the same time."
            )

        if type(inputs) != list:
            inputs = [inputs]

        # In case when model is trained with multiple inputs, pipeline receives list of inputs. (e.g. ImageTextClassification)
        with torch.no_grad():
            if self.model_type == "ImageTextClassifier":
                if type(inputs[0]) != list:
                    inputs = list(map(lambda x: [x], inputs))

                if only_backbone:
                    backbone_output = self.pretrained_model.forward(
                        *inputs, eval=True, classifier=False
                    )
                    return backbone_output.float().detach().cpu().numpy()
                elif last_embedding:
                    if (
                        self.pretrained_model.classifier_head.__class__.__name__
                        != "Base2LinearClassifier"
                    ):
                        raise ValueError(
                            "last_embedding is only supported for Base2LinearClassifier."
                        )
                    backbone_output = self.pretrained_model.forward(
                        *inputs, eval=True, classifier=False
                    )
                    emb = self.pretrained_model.classifier_head.fc_layer1(
                        backbone_output.float()
                    )
                    emb = self.pretrained_model.classifier_head.bn1(emb)
                    emb = F.relu(emb)
                    return emb.detach().cpu().numpy()
                with torch.autocast(self.autocast_device):
                    logits = self.pretrained_model.forward(*inputs, eval=True)
            else:
                if self.model_type == "ImageClassifier":
                    if only_backbone:
                        backbone_output = self.pretrained_model.forward(
                            inputs, eval=True, classifier=False
                        )
                        return backbone_output.float().detach().cpu().numpy()
                    elif last_embedding:
                        if (
                            self.pretrained_model.classifier_head.__class__.__name__
                            != "Base2LinearClassifier"
                        ):
                            raise ValueError(
                                "last_embedding is only supported for Base2LinearClassifier."
                            )
                        backbone_output = self.pretrained_model.forward(
                            inputs, eval=True, classifier=False
                        )
                        emb = self.pretrained_model.classifier_head.fc_layer1(
                            backbone_output.float()
                        )
                        emb = self.pretrained_model.classifier_head.bn1(emb)
                        emb = F.relu(emb)
                        return emb.detach().cpu().numpy()
                    logits = self.pretrained_model.forward(inputs, eval=True)
                else:
                    if only_backbone:
                        backbone_output = self.pretrained_model.forward(
                            inputs, eval=True, classifier=False
                        )
                        return backbone_output.float().detach().cpu().numpy()
                    elif last_embedding:
                        if (
                            self.pretrained_model.classifier_head.__class__.__name__
                            != "Base2LinearClassifier"
                        ):
                            raise ValueError(
                                "last_embedding is only supported for Base2LinearClassifier."
                            )
                        backbone_output = self.pretrained_model.forward(
                            inputs, eval=True, classifier=False
                        )
                        emb = self.pretrained_model.classifier_head.fc_layer1(
                            backbone_output.float()
                        )
                        emb = self.pretrained_model.classifier_head.bn1(emb)
                        emb = F.relu(emb)
                        return emb.detach().cpu().numpy()
                    with torch.autocast(self.autocast_device):
                        logits = self.pretrained_model.forward(inputs, eval=True)

        return postprocess(
            logits,
            topk,
            self.label_name_list,
            return_logits,
            sigmoid,
            temperature,
        )

    def backbone_to_float32(self):
        self.pretrained_model = self.pretrained_model.float()
