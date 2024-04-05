import logging

from ..head_classifier import *
from .text_config import TextClassifierConfig
from ..base_trainer import BaseClassifierModule
from ..base_feedback_trainer import FeedbackBaseClassifierModule

logger = logging.getLogger(__name__)


class TextClassifierModule(BaseClassifierModule):
    """
    Text Classifier for training and inference.

    Args:
        train_config (TextClassifierConfig): TextClassifierConfig.
    """

    def __init__(self, train_config: TextClassifierConfig):
        super().__init__(train_config)

        (
            self.backbone,
            self.tokenizer,
            self.initial_config,
            self.delete_input_key_list,
        ) = self.get_model()
        self.embedding_size = self.initial_config.hidden_size

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
        Get backbone, tokenizer, initial_config, delete_input_key_list
        """
        return self.get_text_model(
            self.train_config.backbone_name,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.lora_r,
            self.train_config.lora_alpha,
            self.train_config.lora_target_modules,
            self.train_config.lora_dropout,
        )

    # model forward
    def forward(
        self,
        input_texts,
        backbone=None,
        classifier_head=None,
        eval=False,
        classifier=True,
    ):
        if backbone is None:
            backbone = self.backbone
        if classifier_head is None:
            classifier_head = self.classifier_head
        return self.text_forward(
            input_texts,
            backbone,
            classifier_head,
            self.initial_config,
            self.train_config.freeze,
            eval=eval,
            classifier=classifier,
        )

    # Optimizer setup
    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.backbone,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.backbone_learning_rate,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer, self.train_config.lr_scheduler)

        return [optimizer], [{"scheduler": lr_scheduler}]


class FeedbackTextClassifierModule(FeedbackBaseClassifierModule):
    """ "
    FeedbackText Classifier for training and inference.

    Args:
        train_config (TextClassifierConfig): TextClassifierConfig.
    """

    def __init__(self, train_config: TextClassifierConfig):
        super().__init__(train_config)

        (
            self.backbone,
            self.tokenizer,
            self.initial_config,
            self.delete_input_key_list,
        ) = self.get_model()
        self.embedding_size = self.initial_config.hidden_size

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
        Get backbone, tokenizer, initial_config, delete_input_key_list
        """
        return self.get_text_model(
            self.train_config.backbone_name,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.lora_r,
            self.train_config.lora_alpha,
            self.train_config.lora_target_modules,
            self.train_config.lora_dropout,
        )

    # model forward
    def forward(
        self,
        input_texts,
        backbone=None,
        classifier_head=None,
        eval=False,
        classifier=True,
    ):
        if backbone is None:
            if type(self.backbone) == nn.ModuleList:
                backbone = self.backbone[0]
            else:
                backbone = self.backbone
        if classifier_head is None:
            classifier_head = self.classifier_head
        return self.text_forward(
            input_texts,
            backbone,
            classifier_head,
            self.initial_config,
            self.train_config.freeze,
            eval=eval,
            classifier=classifier,
        )

    # Optimizer setup
    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.backbone,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.backbone_learning_rate,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer, self.train_config.lr_scheduler)

        return [optimizer], [{"scheduler": lr_scheduler}]
