import logging
import torch.nn as nn
from typing import Union, List

from ..losses import LOSSES

logger = logging.getLogger(__name__)


class BaseClassifierConfig:
    """
    Base Classifier Config Class

    Args:
        batch_size (int): batch size per GPU, default: 32
        max_epochs (int): max epoch for training, default: 10
        feedback_iteration (int): feedback iteration, only used for feedback_training, default: 100.
        e.g. 100 feed back iterations and 5 label, 10 feedback sample -> 100 * 5 * 10 = 5000 samples will be used in train dataset.
        seed (int): random seed, default: 42
        num_class (int): number of class, default: 0
        output_dir (str): output directory, default: 'tmp_classifier'
        device (str): device name, e.g. 'cpu', 'gpu', default: 'gpu'
        use_device_list (Union[str, List[int]]): device list, e.g. 'auto', [0, 1], default: 'auto'
        num_workers (int): number of workers, default: 4
        fc_classifier (Union[str, nn.Module]): fully connected classifier, e.g. 'Base2LinearClassifier', default: 'Base2LinearClassifier'
        label_smoothing_factor (float): label smoothing factor, default: 0.1
        feedback_ema_decay (float): feedback ema decay, default: 0.9
        gradient_accumulation_steps (int): gradient accumulation steps, default: 1
        print_topk_list (tuple): topk tuple for printing, default: (1, 3, 5)
        monitor_topk (Union[int, str]): topk for monitoring, default: 1
        save_ckpt_topk (int): topk for saving checkpoint, default: 3
        check_val_every_n_epoch (int): check validation every n epoch, default: 1
        val_check_interval(int): check validation every n train steps, also saving model checkpoint. default: None,
        num_sanity_val_steps (int): number of sanity validation steps, default: 2
        precision (str): precision, e.g. '16-mixed', '32', default: '16-mixed'
        label_name_list (list): label name list, default: None
        criterion (str): criterion name, e.g. 'cross_entropy', 'focal_loss', default: 'cross_entropy'
        problem_type (str): problem type, e.g. 'single_label_classification', 'multi_label_classification', default: 'single_label_classification'
    """

    def __init__(
        self,
        batch_size: int = 32,
        max_epochs: int = 10,
        feedback_iteration: int = 100,
        seed: int = 42,
        num_class: int = 0,
        output_dir: str = "tmp_classifier",
        device: str = "gpu",
        use_device_list: Union[str, List[int]] = "auto",
        num_workers: int = 4,
        fc_classifier: Union[str, nn.Module] = "Base2LinearClassifier",
        label_smoothing_factor: float = 0.1,
        feedback_ema_decay: float = 0.9,
        gradient_accumulation_steps: int = 1,
        print_topk_list: tuple = (1, 3, 5),
        monitor_topk: Union[int, str] = 1,
        save_ckpt_topk: int = 3,
        check_val_every_n_epoch: int = 1,
        val_check_interval: int = None,
        num_sanity_val_steps: int = 2,
        precision: str = "16-mixed",
        label_name_list: list = None,
        criterion: str = "cross_entropy",
        problem_type: str = "single_label_classification",
        lr_scheduler: str = "linear_warmup",
    ):
        # Batch size per GPU
        self.batch_size = batch_size
        # Max epoch for training
        self.max_epochs = max_epochs
        # Feedback iteration, only used for feedback_training
        self.feedback_iteration = feedback_iteration
        self.seed = seed
        # Num class will be define and be checked at trainer class
        self.num_class = num_class
        self.output_dir = output_dir
        self.device = device
        # Can be GPU Device number e.g. [0, 1]
        self.use_device_list = use_device_list
        self.num_workers = num_workers
        # Can be classifier name string or defined nn.Moudle
        self.fc_classifier = fc_classifier
        self.label_smoothing_factor = label_smoothing_factor
        self.feedback_ema_decay = feedback_ema_decay
        self.gradient_accumulation_steps = gradient_accumulation_steps

        self.print_topk_list = list(print_topk_list)
        if monitor_topk != "total" and monitor_topk not in print_topk_list:
            raise ValueError("monitor_topk must be in print_topk_list or 'total'")

        self.monitor_topk = monitor_topk
        self.save_ckpt_topk = save_ckpt_topk
        self.check_val_every_n_epoch = check_val_every_n_epoch
        self.val_check_interval = val_check_interval
        self.num_sanity_val_steps = num_sanity_val_steps
        self.precision = precision
        self.label_name_list = label_name_list

        if problem_type not in [
            "single_label_classification",
            "multi_label_classification",
        ]:
            raise ValueError(
                "problem_type must be 'single_label_classification' or 'multi_label_classification'"
            )
        self.problem_type = problem_type

        if criterion not in LOSSES.keys():
            raise ValueError(f"criterion must be in {LOSSES.keys()}")

        if problem_type == "multi_label_classification":
            if criterion not in ["binary_cross_entropy", "binary_focal_loss"]:
                raise ValueError(
                    f"criterion must be in ['binary_cross_entropy', 'binary_focal_loss'] for multi_label_classification"
                )

        if criterion == "focal_loss" and label_smoothing_factor > 0:
            criterion = "focal_loss_with_label_smoothing"
        self.criterion = criterion

        if lr_scheduler not in ["linear_warmup", "constant"]:
            raise ValueError(f"lr_scheduler must be in ['linear_warmup', 'constant']")
        self.lr_scheduler = lr_scheduler

    def to_dict(self):
        """
        Convert class attributes to dictionary
        """
        return self.__dict__
