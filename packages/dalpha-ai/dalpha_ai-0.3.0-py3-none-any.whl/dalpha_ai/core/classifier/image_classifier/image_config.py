import logging
from ..base_config import BaseClassifierConfig

logger = logging.getLogger(__name__)


class ImageClassifierConfig(BaseClassifierConfig):
    """
    Image Classifier Config.
    Containing all the hyperparameters for training and inference.

    Args:
        backbone_name (str): Name of the backbone model. Defaults to "eva_large_patch14_196.in22k_ft_in22k_in1k".
        classifier_learning_rate (float): Learning rate for the classifier. Defaults to 1e-3.
        backbone_learning_rate (float): Learning rate for the backbone. Defaults to 4e-5.
        freeze (bool): Freeze the backbone. Defaults to False.
        lora (bool): Use LoRA. Defaults to False.
        lora_r (int): LoRA r. Defaults to 16.
        lora_alpha (int): LoRA alpha. Defaults to 16.
        lora_target_modules (list): LoRA target modules. Defaults to ["qkv"].
        lora_dropout (float): LoRA dropout. Defaults to 0.1.
        auto_augment (str): Image augmentation method. Defaults to "rand-n3-mstd1".
        crop_ratio (float): Minimum crop ratio for when augmentate image, default: 0.9.
    """

    def __init__(
        self,
        backbone_name: str = "eva_large_patch14_196.in22k_ft_in22k_in1k",
        classifier_learning_rate: float = 1e-3,
        backbone_learning_rate: float = 4e-5,
        freeze: bool = False,
        lora: bool = False,
        lora_r: int = 16,
        lora_alpha: int = 16,
        lora_target_modules: list = None,
        lora_dropout: float = 0.1,
        auto_augment: str = "rand-n3-mstd1",
        crop_ratio: float = 0.9,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.backbone_name = backbone_name
        self.classifier_learning_rate = classifier_learning_rate
        self.backbone_learning_rate = backbone_learning_rate
        self.freeze = freeze
        self.lora = lora
        if self.freeze and self.lora:
            raise ValueError(
                "freezing backbone and using lora cannot be True at the same time"
            )

        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        if lora_target_modules is None:
            self.lora_target_modules = ["qkv"]
        else:
            self.lora_target_modules = lora_target_modules
        self.lora_dropout = lora_dropout

        # Image augmentation method
        self.auto_augment = auto_augment
        self.crop_ratio = crop_ratio
        # Boolean to check if the model is loaded from transformers or timm, will be set in trainer
        self.timm = None


class ImageClassifierConfig(BaseClassifierConfig):
    """
    Image Classifier Config.
    Containing all the hyperparameters for training and inference.

    Args:
        backbone_name (str): Name of the backbone model. Defaults to "eva_large_patch14_196.in22k_ft_in22k_in1k".
        classifier_learning_rate (float): Learning rate for the classifier. Defaults to 1e-3.
        backbone_learning_rate (float): Learning rate for the backbone. Defaults to 4e-5.
        freeze (bool): Freeze the backbone. Defaults to False.
        lora (bool): Use LoRA. Defaults to False.
        lora_r (int): LoRA r. Defaults to 16.
        lora_alpha (int): LoRA alpha. Defaults to 16.
        lora_target_modules (str): LoRA target modules. Defaults to ["qkv"].
        lora_dropout (float): LoRA dropout. Defaults to 0.1.
        auto_augment (str): Image augmentation method. Defaults to "rand-n3-mstd1".
        crop_ratio (float): Minimum crop ratio for when augmentate image, default: 0.9.
    """

    def __init__(
        self,
        backbone_name: str = "eva_large_patch14_196.in22k_ft_in22k_in1k",
        classifier_learning_rate: float = 1e-3,
        backbone_learning_rate: float = 4e-5,
        freeze: bool = False,
        lora: bool = False,
        lora_r: int = 16,
        lora_alpha: int = 16,
        lora_target_modules: str = ["qkv"],
        lora_dropout: float = 0.1,
        auto_augment: str = "rand-n3-mstd1",
        crop_ratio: float = 0.9,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.backbone_name = backbone_name
        self.classifier_learning_rate = classifier_learning_rate
        self.backbone_learning_rate = backbone_learning_rate
        self.freeze = freeze
        self.lora = lora
        if self.freeze and self.lora:
            raise ValueError(
                "freezing backbone and using lora cannot be True at the same time"
            )

        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        self.lora_target_modules = lora_target_modules
        self.lora_dropout = lora_dropout

        # Image augmentation method
        self.auto_augment = auto_augment
        self.crop_ratio = crop_ratio
        # Boolean to check if the model is loaded from transformers or timm, will be set in trainer
        self.timm = None
