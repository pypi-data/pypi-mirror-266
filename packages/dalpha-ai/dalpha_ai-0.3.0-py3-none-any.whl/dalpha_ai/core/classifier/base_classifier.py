import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import copy
import torch

torch.backends.cudnn.benchmark = False
import logging
from typing import List, Union

import pandas as pd
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint

from .trainer_util import set_seed, sample_stratified

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def check_dataset(dataset: Union[pd.DataFrame, List[List]], column_list: List[str], train_config=None):
    """
    Check if the dataset is in the correct format
    Args:
        dataset (pd.DataFrame or list): dataset
        column_list (list): list of column names (must be in order of text, label)
    Returns:
        output dataset
    """

    if train_config != None:
        if train_config.problem_type == "multi_label_classification":
            try:
                dataset['label'] = dataset['label'].apply(lambda x: eval(x))
            except:
                raise ValueError(
                    f"cannot convert dataset"
                )

    if type(dataset) == pd.DataFrame:
        if len(dataset.columns) != len(column_list):
            raise ValueError(
                f"For DataFrame input, dataset must have {len(column_list)} columns. Got {len(dataset.columns)} columns"
            )
        for idx, col in enumerate(column_list):
            if dataset.columns[idx] != col:
                logger.warning(
                    f"Column {idx} is {dataset.columns[idx]}, but expected {col}"
                )
            dataset.rename(columns={dataset.columns[idx]: col}, inplace=True)
    elif type(dataset) == list:
        if len(dataset[0]) != len(column_list):
            raise ValueError(
                f"For list input, dataset must have {len(column_list)} columns. Got {len(dataset[0])} columns"
            )
        else:
            logger.warning(
                f"For list input, column names will be set to default: {column_list}"
            )
    else:
        raise ValueError(
            f"Dataset must be either pd.DataFrame or list. Got {type(dataset)}"
        )
    
    if dataset["label"].dtype == "object":
        if not type(dataset["label"][0]) == list:
            raise ValueError(
                f"Multi Label column must be list type. Got {type(dataset['label'][0])}"
            )
        elif not type(dataset["label"][0][0]) == int:
            raise ValueError(
                f"Element of Multi Label column must be int type. Got {type(dataset['label'][0][0])}"
            )    

    elif dataset["label"].dtype != "int64":
        raise ValueError(
            f"Label column must be int64 dtype. Got {dataset['label'].dtype}"
        )

    return dataset


class BaseClassifier:
    """
    Base class for all classifiers, including text, image, and image-text classifiers
    Args:
        train_dataset (pd.DataFrame or list): training dataset
        val_dataset (pd.DataFrame or list): validation dataset
        feedback_dataset (pd.DataFrame or list): feedback dataset (optional)
        test_dataset (pd.DataFrame or list): test dataset (optional)
        label_name_list (list): list of label names (optional)
        train_config (ClassifierConfig): training config (optional)
    """

    def __init__(
        self,
        train_dataset: Union[pd.DataFrame, List[List]],
        val_dataset: Union[pd.DataFrame, List[List]],
        feedback_dataset: Union[pd.DataFrame, List[List]] = None,
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List = None,
        train_config=None,
    ):
        from .text_classifier import TextClassifierConfig
        from .image_classifier import ImageClassifierConfig
        from .image_text_classifier import ImageTextClassifierConfig

        self.train_config = train_config
        # Set random seed
        set_seed(self.train_config.seed)

        train_dataset = copy.deepcopy(train_dataset)
        val_dataset = copy.deepcopy(val_dataset)
        feedback_dataset = copy.deepcopy(feedback_dataset)
        test_dataset = copy.deepcopy(test_dataset)
        if type(train_config) == TextClassifierConfig:
            train_dataset = check_dataset(train_dataset, ["text", "label"], train_config)
            val_dataset = check_dataset(val_dataset, ["text", "label"], train_config)
            if feedback_dataset is not None:
                feedback_dataset = check_dataset(
                    feedback_dataset, ["text", "label"], train_config
                )
            if test_dataset is not None:
                test_dataset = check_dataset(test_dataset, ["text", "label"], train_config)
            else:
                logger.warning(
                    "test_dataset is None. Using val_dataset as test_dataset"
                )
                test_dataset = copy.deepcopy(val_dataset)


        elif type(train_config) == ImageClassifierConfig:
            train_dataset = check_dataset(train_dataset, ["img_path", "label"], train_config)
            val_dataset = check_dataset(val_dataset, ["img_path", "label"], train_config)
            if feedback_dataset is not None:
                feedback_dataset = check_dataset(
                    feedback_dataset, ["img_path", "label"], train_config
                )
            if test_dataset is not None:
                test_dataset = check_dataset(test_dataset, ["img_path", "label"], train_config)
            else:
                logger.warning(
                    "test_dataset is None. Using val_dataset as test_dataset"
                )
                test_dataset = copy.deepcopy(val_dataset)

        elif type(train_config) == ImageTextClassifierConfig:
            train_dataset = check_dataset(train_dataset, ["img_path", "text", "label"], train_config)
            val_dataset = check_dataset(val_dataset, ["img_path", "text", "label"], train_config)
            if feedback_dataset is not None:
                feedback_dataset = check_dataset(
                    feedback_dataset, ["img_path", "text", "label"], train_config
                )
            if test_dataset is not None:
                test_dataset = check_dataset(
                    test_dataset, ["img_path", "text", "label"], train_config
                )
            else:
                logger.warning(
                    "test_dataset is None. Using val_dataset as test_dataset"
                )
                test_dataset = copy.deepcopy(val_dataset)
        else:
            raise ValueError(f"Not supported train_config type: {type(train_config)}")
        
        ## If feedback_dataset exists, concat feedback dataset and stratified sample from train dataset
        if feedback_dataset is not None:
            sampled_train_dataset = sample_stratified(train_dataset, self.train_config.feedback_iteration * len(feedback_dataset), self.train_config.problem_type)
            # Add feedback label for distinguishing feedback data
            sampled_train_dataset["feedback_flag"] = [0] * len(sampled_train_dataset)
            repeated_feedback_dataset = pd.concat([feedback_dataset] * self.train_config.feedback_iteration, ignore_index=True)
            repeated_feedback_dataset["feedback_flag"] = [1] * len(repeated_feedback_dataset)
            self.train_dataset = pd.concat([sampled_train_dataset, repeated_feedback_dataset], ignore_index=True)
        else:
            self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset

        # Check number of class when training config num class value is default value.
        if self.train_config.num_class == 0:
            if label_name_list is not None:
                logger.info("Get number of class with the length of label name list.")
                self.train_config.num_class = len(label_name_list)
                self.train_config.label_name_list = label_name_list
            else:
                label_list = (
                    list(map(lambda x: int(x), train_dataset["label"]))
                    + list(map(lambda x: int(x), val_dataset["label"]))
                    + list(map(lambda x: int(x), test_dataset["label"]))
                )
                self.train_config.num_class = max(label_list) + 1
                logger.warning(
                    f"Since training config does not get the number of class, trainer estimate the number of class with input dataset, estimated number of class is {self.train_config.num_class} "
                )

        else:
            if label_name_list is not None:
                if self.train_config.num_class != len(label_name_list):
                    raise ValueError(
                        f"Number of class in training config {self.train_config.num_class} does not match with length of label_name_list {len(label_name_list)}."
                    )
                self.train_config.label_name_list = label_name_list

        self.trainer = None

    def base_train(self):
        """
        Base training function
        """
        if self.train_config.problem_type == "single_label_classification":
            if self.train_config.monitor_topk == "total":
                monitor_acc = "val/tot_acc"
                if self.train_config.val_check_interval:
                    filename = "epoch{epoch:02d}-step{step}-val_totacc={val/tot_acc:.4f}"
                else:
                    filename = "epoch{epoch:02d}-val_totacc={val/tot_acc:.4f}"
                checkpoint_callback = ModelCheckpoint(
                    monitor=monitor_acc,
                    mode="max",
                    save_top_k=self.train_config.save_ckpt_topk,
                    filename=filename,
                    auto_insert_metric_name=False,
                )
            else:
                monitor_acc = f"val/acc{self.train_config.monitor_topk}"
                if self.train_config.val_check_interval:
                    filename = "epoch{epoch:02d}-step{step}-val_acc={val/monitor_acc:.4f}"
                else:
                    filename = "epoch{epoch:02d}-val_acc={val/monitor_acc:.4f}"
                checkpoint_callback = ModelCheckpoint(
                    monitor=monitor_acc,
                    mode="max",
                    save_top_k=self.train_config.save_ckpt_topk,
                    filename=filename,
                    auto_insert_metric_name=False,
                )
        else:
            monitor_f1 = f"val/f1"
            if self.train_config.val_check_interval:
                filename = "epoch{epoch:02d}-step{step}-val_f1={val/f1:.4f}"
            else:
                filename = "epoch{epoch:02d}-val_f1={val/f1:.4f}"
            checkpoint_callback = ModelCheckpoint(
                monitor=monitor_f1,
                mode="max",
                save_top_k=self.train_config.save_ckpt_topk,
                filename=filename,
                auto_insert_metric_name=False,
            )

        # Define trainer
        self.trainer = pl.Trainer(
            accelerator=self.train_config.device,
            devices=self.train_config.use_device_list,
            precision=self.train_config.precision,
            max_epochs=self.train_config.max_epochs,
            callbacks=[checkpoint_callback],
            num_sanity_val_steps=self.train_config.num_sanity_val_steps,
            check_val_every_n_epoch=self.train_config.check_val_every_n_epoch,
            val_check_interval=self.train_config.val_check_interval,
            default_root_dir=self.train_config.output_dir,
            strategy="ddp_find_unused_parameters_true",
        )

        self.trainer.fit(self.train_module, self.data_module)

        print(
            "Best ckpt saved path: ", self.trainer.checkpoint_callback.best_model_path
        )

    # Test the best trained model with test dataset
    def test(self):
        """
        Test the best trained model with test dataset, if test dataset is None, test with val dataset.
        """
        if self.trainer is None:
            raise ValueError(
                "You should train the trainer before inference. E.g. TextClassifier().train()"
            )
        self.trainer.test(ckpt_path="best", dataloaders=self.data_module)
