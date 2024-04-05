import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch

torch.backends.cudnn.benchmark = False
import logging
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import pytorch_lightning as pl

from ..trainer_util import set_seed
from .image_config import ImageClassifierConfig
from .image_datamodule import (
    ImageClassifierDataModule,
    FeedbackImageClassifierDataModule,
)
from .image_trainer import ImageClassifierModule, FeedbackImageClassifierModule
from ..base_classifier import BaseClassifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class ImageClassifier(BaseClassifier):
    """
    Image Classifier for training and inference.

    Args:
        train_dataset (Union[pd.DataFrame, List[List]]): Training dataset.
        val_dataset (Union[pd.DataFrame, List[List]]): Validation dataset.
        test_dataset (Union[pd.DataFrame, List[List]], optional): Test dataset. Defaults to None.
        label_name_list (List, optional): List of label names. Defaults to None.
        train_config (ImageClassifierConfig, optional): ImageClassifierConfig. Defaults to None.
    """

    def __init__(
        self,
        train_dataset: Union[pd.DataFrame, List[List]],
        val_dataset: Union[pd.DataFrame, List[List]],
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List = None,
        train_config: ImageClassifierConfig = None,
    ):
        # Initial starting without loading from checkpoint
        if train_config is None:
            output_dir = "tmp_classifier"
            logger.info(
                f"No `ImageClassifierConfig` passed, using `output_dir={output_dir}`."
            )
            train_config = ImageClassifierConfig(output_dir=output_dir)

        else:
            if type(train_config) != ImageClassifierConfig:
                raise ValueError(
                    f"train_config should be ImageClassifierConfig, but got {type(train_config)}"
                )

        feedback_dataset = None
        super().__init__(
            train_dataset,
            val_dataset,
            feedback_dataset,
            test_dataset,
            label_name_list,
            train_config,
        )

        # Define Data module
        self.data_module = ImageClassifierDataModule(
            train_dataset=self.train_dataset,
            val_dataset=self.val_dataset,
            test_dataset=self.test_dataset,
            train_config=self.train_config,
        )

        # Define Train Module
        self.train_module = ImageClassifierModule(train_config=self.train_config)

        self.trainer = None

    def train(self, resume_from_checkpoint: Optional[str] = None):
        # Resume from checkpoint, local path to a saved checkpoint.
        if resume_from_checkpoint:
            self.train_module = ImageClassifierModule.load_from_checkpoint(
                resume_from_checkpoint, train_config=self.train_config
            )
        # Define Trainer and Callbacks for training, and start training
        self.base_train()


class FeedbackImageClassifier(BaseClassifier):
    """
    Feedback Image Classifier for training and inference. This class is used for training with additional feedback data.

    Args:
        train_dataset (Union[pd.DataFrame, List[List]]): Training dataset. Recommended to use the original training dataset.
        val_dataset (Union[pd.DataFrame, List[List]]): Validation dataset. Recommended to use the original validation dataset.
        feedback_dataset (Union[pd.DataFrame, List[List]]): Feedback dataset. It's okay even if the dataset consists of fewer than 10 items.
        test_dataset (Union[pd.DataFrame, List[List]], optional): Test dataset. Defaults to None.
        label_name_list (List, optional): List of label names. Defaults to None.
        train_config (ImageClassifierConfig, optional): ImageClassifierConfig. Defaults to None.
    """

    def __init__(
        self,
        train_dataset: Union[pd.DataFrame, List[List]],
        val_dataset: Union[pd.DataFrame, List[List]],
        feedback_dataset: Union[pd.DataFrame, List[List]],
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List = None,
        train_config: ImageClassifierConfig = None,
    ):
        # Initial starting without loading from checkpoint
        if train_config is None:
            output_dir = "tmp_classifier"
            logger.info(
                f"No `ImageClassifierConfig` passed, using `output_dir={output_dir}`."
            )
            train_config = ImageClassifierConfig(output_dir=output_dir)

        else:
            if type(train_config) != ImageClassifierConfig:
                raise ValueError(
                    f"train_config should be ImageClassifierConfig, but got {type(train_config)}"
                )

        super().__init__(
            train_dataset,
            val_dataset,
            feedback_dataset,
            test_dataset,
            label_name_list,
            train_config,
        )

        # Define Data module
        self.data_module = FeedbackImageClassifierDataModule(
            train_dataset=self.train_dataset,
            val_dataset=self.val_dataset,
            test_dataset=self.test_dataset,
            train_config=self.train_config,
        )

        # Define Train Module
        self.train_module = FeedbackImageClassifierModule(
            train_config=self.train_config
        )

        self.trainer = None

    def train(self, resume_from_checkpoint=None):
        # Resume from checkpoint, local path to a saved checkpoint. Original checkpoint is required for feedback training.
        if resume_from_checkpoint is None:
            raise ValueError(
                "resume_from_checkpoint should be provided for feedback training."
            )

        self.train_module = FeedbackImageClassifierModule.load_from_checkpoint(
            resume_from_checkpoint, train_config=self.train_config
        )
        # Define Trainer and Callbacks for training, and start training
        self.base_train()
