import torch
import logging

logger = logging.getLogger(__name__)


class ZeroshotImageClassifierConfig:
    """
    Zeroshot Image Classifier Config

    Args:
        backbone_name (str): backbone name
        model_name (str): model name
    """

    def __init__(
        self,
        backbone_name: str = "clip",
        model_name: str = "patrickjohncyh/fashion-clip",
    ):
        self.device = "cuda"

        self.num_class = 0
        self.output_dir = "tmp_classifier"
        self.num_workers = 4
        self.text_prompt = "This is a photo of {}"

        self.backbone_name = backbone_name  # "clip"
        self.model_name = model_name  # "patrickjohncyh/fashion-clip"
        self.embedding_size = 512

        self.print_topk_list = [1, 3, 5]
        self.label_name_list = None
