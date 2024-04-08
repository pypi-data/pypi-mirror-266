import torch
from ..head_classifier import *

from .image_text_config import ImageTextClassifierConfig
from ..base_trainer import BaseClassifierModule
from ..base_feedback_trainer import FeedbackBaseClassifierModule


class ImageTextClassifierModule(BaseClassifierModule):
    """
    Image Text Classifier Module.

    Args:
        train_config (ImageTextClassifierConfig): ImageTextClassifierConfig.
    """

    def __init__(self, train_config: ImageTextClassifierConfig):
        super().__init__(train_config)

        (
            self.image_backbone,
            self.train_transforms,
            self.val_transforms,
            self.image_data_config,
            self.train_config.image_timm,
            self.image_initial_config,
            self.text_backbone,
            self.tokenizer,
            self.text_initial_config,
            self.delete_input_key_list,
        ) = self.get_model()
        # Concat embedding
        self.image_embedding_size = self.image_backbone.forward(
            torch.randn(self.image_data_config["input_size"]).unsqueeze(0)
        ).shape[-1]
        self.text_embedding_size = self.text_initial_config.hidden_size
        self.embedding_size = self.image_embedding_size + self.text_embedding_size

        # Define classifier
        if type(self.train_config.fc_classifier) == str:
            classifier_class = globals()[self.train_config.fc_classifier]
            self.classifier_head = classifier_class(
                self.embedding_size, self.train_config.num_class
            )
        else:
            self.classifier_head = self.train_config.fc_classifier(
                self.embedding_size, self.train_config.num_class
            )

        self.save_hyperparameters()

    def get_model(self):
        """
        Get model from config.
        Return image_backbone, train_transforms, val_transforms, image_initial_config, image_timm, text_backbone, tokenizer, text_initial_config, delete_input_key_list
        """
        # Get Text Models
        get_text_model_result = self.get_text_model(
            self.train_config.text_backbone_name,
            self.train_config.text_freeze,
            self.train_config.text_lora,
            self.train_config.text_lora_r,
            self.train_config.text_lora_alpha,
            self.train_config.text_lora_target_modules,
            self.train_config.text_lora_dropout,
        )
        get_image_model_result = self.get_image_model(
            self.train_config.image_backbone_name,
            self.train_config.image_freeze,
            self.train_config.image_lora,
            self.train_config.image_lora_r,
            self.train_config.image_lora_alpha,
            self.train_config.image_lora_target_modules,
            self.train_config.image_lora_dropout,
        )

        return get_image_model_result + get_text_model_result

    # model forward
    def forward(
        self,
        input_img_paths,
        input_texts,
        image_backbone=None,
        text_backbone=None,
        classifier_head=None,
        eval=False,
        classifier=True,
    ):
        if image_backbone is None:
            image_backbone = self.image_backbone
        if text_backbone is None:
            text_backbone = self.text_backbone
        if classifier_head is None:
            classifier_head = self.classifier_head
        image_backbone_outputs = self.image_forward(
            input_img_paths,
            image_backbone,
            classifier_head,
            self.train_config.image_freeze,
            eval=eval,
            classifier=False,
        )
        text_backbone_outputs = self.text_forward(
            input_texts,
            text_backbone,
            classifier_head,
            self.text_initial_config,
            self.train_config.text_freeze,
            eval=eval,
            classifier=False,
        )

        backbone_outputs = torch.cat(
            [image_backbone_outputs, text_backbone_outputs], dim=1
        )
        if classifier:
            logits = classifier_head(backbone_outputs)

            return logits
        else:
            return backbone_outputs

    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.text_backbone,
            self.train_config.text_freeze,
            self.train_config.text_lora,
            self.train_config.text_backbone_learning_rate,
        )
        optimizer = self.add_optimizers(
            optimizer,
            self.image_backbone,
            self.train_config.image_freeze,
            self.train_config.image_lora,
            self.train_config.image_backbone_learning_rate,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer, self.train_config.lr_scheduler)

        return [optimizer], [{"scheduler": lr_scheduler}]


class FeedbackImageTextClassifierModule(FeedbackBaseClassifierModule):
    """
    Feedback Image Text Classifier Module.

    Args:
        train_config (ImageTextClassifierConfig): ImageTextClassifierConfig.
    """

    def __init__(self, train_config: ImageTextClassifierConfig):
        super().__init__(train_config)

        (
            self.image_backbone,
            self.train_transforms,
            self.val_transforms,
            self.image_data_config,
            self.train_config.image_timm,
            self.image_initial_config,
            self.text_backbone,
            self.tokenizer,
            self.text_initial_config,
            self.delete_input_key_list,
        ) = self.get_model()
        # Concat embedding
        self.image_embedding_size = self.image_backbone.forward(
            torch.randn(self.image_data_config["input_size"]).unsqueeze(0)
        ).shape[-1]
        self.text_embedding_size = self.text_initial_config.hidden_size
        self.embedding_size = self.image_embedding_size + self.text_embedding_size

        # Define classifier
        if type(self.train_config.fc_classifier) == str:
            classifier_class = globals()[self.train_config.fc_classifier]
            self.classifier_head = classifier_class(
                self.embedding_size, self.train_config.num_class
            )
        else:
            self.classifier_head = self.train_config.fc_classifier(
                self.embedding_size, self.train_config.num_class
            )

        self.save_hyperparameters()

    def get_model(self):
        """
        Get model from config.
        Return image_backbone, train_transforms, val_transforms, image_initial_config, image_timm, text_backbone, tokenizer, text_initial_config, delete_input_key_list
        """
        # Get Text Models
        get_text_model_result = self.get_text_model(
            self.train_config.text_backbone_name,
            self.train_config.text_freeze,
            self.train_config.text_lora,
            self.train_config.text_lora_r,
            self.train_config.text_lora_alpha,
            self.train_config.text_lora_target_modules,
            self.train_config.text_lora_dropout,
        )
        get_image_model_result = self.get_image_model(
            self.train_config.image_backbone_name,
            self.train_config.image_freeze,
            self.train_config.image_lora,
            self.train_config.image_lora_r,
            self.train_config.image_lora_alpha,
            self.train_config.image_lora_target_modules,
            self.train_config.image_lora_dropout,
        )

        return get_image_model_result + get_text_model_result

    # model forward
    def forward(
        self,
        input_img_paths,
        input_texts,
        image_backbone=None,
        text_backbone=None,
        classifier_head=None,
        eval=False,
        classifier=True,
    ):
        if image_backbone is None:
            image_backbone = self.image_backbone
        if text_backbone is None:
            text_backbone = self.text_backbone
        if classifier_head is None:
            classifier_head = self.classifier_head
        image_backbone_outputs = self.image_forward(
            input_img_paths,
            image_backbone,
            classifier_head,
            self.train_config.image_freeze,
            eval=eval,
            classifier=False,
        )
        text_backbone_outputs = self.text_forward(
            input_texts,
            text_backbone,
            classifier_head,
            self.text_initial_config,
            self.train_config.text_freeze,
            eval=eval,
            classifier=False,
        )

        backbone_outputs = torch.cat(
            [image_backbone_outputs, text_backbone_outputs], dim=1
        )
        if classifier:
            logits = classifier_head(backbone_outputs)

            return logits
        else:
            return backbone_outputs

    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.text_backbone,
            self.train_config.text_freeze,
            self.train_config.text_lora,
            self.train_config.text_backbone_learning_rate,
        )
        optimizer = self.add_optimizers(
            optimizer,
            self.image_backbone,
            self.train_config.image_freeze,
            self.train_config.image_lora,
            self.train_config.image_backbone_learning_rate,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer, self.train_config.lr_scheduler)

        return [optimizer], [{"scheduler": lr_scheduler}]
