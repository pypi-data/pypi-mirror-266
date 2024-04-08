import os
import json
import pickle
from typing import Union, List

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
import onnxruntime
from ..classifier.trainer_util import (
    TextClassifierInputPreprocess,
    TextClassifierSelectToken,
    ImageClassifierInputPreprocess,
)
from transformers import AutoTokenizer, AutoConfig
import torch
import torch.nn.functional as F
from easydict import EasyDict

from .onnx_util import onnx_inference, classifier_onnx_preprocess
from .util import postprocess


class OnnxTextClassificationPipeline:
    """
    Onnx Text Classification Pipeline

    Args:
        model_type (str): Model type, only support TextClassifier.
        save_dir (str): Model directory.
        device (str, optional): Device for inference, support cpu and gpu. Defaults to "cpu".
    """

    def __init__(
        self,
        model_type: str,
        save_dir: str,
        device: str = "cpu",
        quantization: bool = False,
        optimization: bool = False,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(save_dir)

        if device == "gpu":
            self.device = torch.device("cuda")
            if quantization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_quantized.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            elif optimization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_optimized.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            else:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            self.classifier_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "classifier_head.onnx"),
                providers=["CUDAExecutionProvider"],
            )
        # cpu mode
        else:
            self.device = torch.device("cpu")
            if quantization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_quantized.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            elif optimization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_optimized.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            else:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            self.classifier_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "classifier_head.onnx"),
                providers=["CPUExecutionProvider"],
            )

        # Load train config
        with open(
            os.path.join(save_dir, "train_config.json"), "r", encoding="utf-8"
        ) as f:
            train_config = EasyDict(json.load(f))
        self.text_prompt = train_config.text_prompt
        self.label_name_list = train_config.label_name_list
        assert (
            train_config.timm == False
        ), "timm model is not supported yet for TextClassificationPipeline"
        self.config = AutoConfig.from_pretrained(save_dir)

        self.classifier_head = torch.load(
            os.path.join(save_dir, "classifier_head.ckpt"), map_location=self.device
        )
        self.classifier_head.eval()

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
            inputs (Union[str, List[str]]): Input text or list of input text.
            topk (int, optional): Top k prediction. Defaults to 1.
            return_logits (bool, optional): Return logits or not. Defaults to False.
            sigmoid (bool, optional): Apply sigmoid or not(Softmax). Defaults to False.
            only_backbone (bool, optional): Only return backbone output embedding. Defaults to False.
        """
        if only_backbone and last_embedding:
            raise ValueError(
                "only_backbone and last_embedding cannot be True at the same time."
            )

        if type(inputs) != list:
            inputs = [inputs]

        preprocessed_inputs = TextClassifierInputPreprocess(
            inputs,
            text_prompt=self.text_prompt,
            device=self.device,
            tokenizer=self.tokenizer,
        )

        embeddings = onnx_inference(self.ort_session, preprocessed_inputs, self.device)

        selected_token_embedding = TextClassifierSelectToken(
            [embeddings], preprocessed_inputs, self.config
        )

        if only_backbone:
            return selected_token_embedding.cpu().detach().numpy()

        elif last_embedding:
            if self.classifier_head.__class__.__name__ != "Base2LinearClassifier":
                raise ValueError(
                    "last_embedding is only supported for Base2LinearClassifier."
                )
            emb = self.classifier_head.fc_layer1(
                selected_token_embedding.to(self.device)
            )
            emb = self.classifier_head.bn1(emb)
            emb = F.relu(emb)
            return emb.detach().cpu().numpy()

        # CLassifier ort input preprocess
        classifier_ort_input_dict = classifier_onnx_preprocess(
            self.classifier_ort_session, selected_token_embedding
        )

        logits = onnx_inference(
            self.classifier_ort_session, classifier_ort_input_dict, self.device
        )

        return postprocess(
            logits, topk, self.label_name_list, return_logits, sigmoid, temperature
        )


class OnnxImageClassificationPipeline:
    """
    Onnx Image Classification Pipeline

    Args:
        model_type (str): Model type, only support ImageClassifier.
        save_dir (str): Model directory.
        device (str, optional): Device for inference, support cpu and gpu. Defaults to "cpu".
    """

    def __init__(
        self,
        model_type: str,
        save_dir: str,
        device: str = "cpu",
        quantization: bool = False,
        optimization: bool = False,
    ):
        if device == "gpu":
            self.device = torch.device("cuda")
            if quantization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_quantized.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            elif optimization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_optimized.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            else:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            self.classifier_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "classifier_head.onnx"),
                providers=["CUDAExecutionProvider"],
            )
        # cpu mode
        else:
            self.device = torch.device("cpu")
            if quantization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_quantized.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            elif optimization:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model_optimized.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            else:
                self.ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "model.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            self.classifier_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "classifier_head.onnx"),
                providers=["CPUExecutionProvider"],
            )
        # Load train config
        with open(
            os.path.join(save_dir, "train_config.json"), "r", encoding="utf-8"
        ) as f:
            train_config = EasyDict(json.load(f))
        self.label_name_list = train_config.label_name_list

        # Load val_transforms
        with open(os.path.join(save_dir, "val_transforms.pkl"), "rb") as f:
            self.transforms = pickle.load(f)

        # Load config
        if os.path.exists(os.path.join(save_dir, "config.json")):
            with open(os.path.join(save_dir, "config.json"), "r") as f:
                self.config = json.load(f)
        else:
            self.config = None

        self.classifier_head = torch.load(
            os.path.join(save_dir, "classifier_head.ckpt"), map_location=self.device
        )
        self.classifier_head.eval()

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
            inputs (Union[str, List[str]]): Input image path or list of input image path.
            topk (int, optional): Top k prediction. Defaults to 1.
            return_logits (bool, optional): Return logits or not. Defaults to False.
            sigmoid (bool, optional): Apply sigmoid or not(Softmax). Defaults to False.
            only_backbone (bool, optional): Only return backbone output embedding. Defaults to False.
        """
        if only_backbone and last_embedding:
            return ValueError(
                "only_backbone and last_embedding cannot be True at the same time."
            )

        if type(inputs) != list:
            inputs = [inputs]

        #  preprocessed_inputs = TextClassifierInputPreprocess(
        #     inputs,
        #     text_prompt=self.text_prompt,
        #     device=self.device,
        #     tokenizer=self.tokenizer,
        # )

        # embeddings = onnx_inference(self.ort_session, preprocessed_inputs, self.device)

        preprocessed_inputs = {
            self.ort_session.get_inputs()[0].name: ImageClassifierInputPreprocess(
                inputs,
                device=self.device,
                transforms=self.transforms,
            )
        }

        embeddings = onnx_inference(self.ort_session, preprocessed_inputs, self.device)

        ### Transformer 사용시에는 select token 과정 필요.
        if self.config:
            if self.config["model_type"] == "vit":
                embeddings = embeddings[:, 0]
            else:
                raise NotImplementedError("Only vit is supported for now")

        if only_backbone:
            return embeddings.cpu().detach().numpy()

        elif last_embedding:
            if self.classifier_head.__class__.__name__ != "Base2LinearClassifier":
                raise ValueError(
                    "last_embedding is only supported for Base2LinearClassifier."
                )
            emb = self.classifier_head.fc_layer1(embeddings.to(self.device))
            emb = self.classifier_head.bn1(emb)
            emb = F.relu(emb)
            return emb.detach().cpu().numpy()

        # CLassifier ort input preprocess
        classifier_ort_input_dict = classifier_onnx_preprocess(
            self.classifier_ort_session, embeddings
        )
        logits = onnx_inference(
            self.classifier_ort_session, classifier_ort_input_dict, self.device
        )

        return postprocess(
            logits, topk, self.label_name_list, return_logits, sigmoid, temperature
        )


class OnnxImageTextClassificationPipeline:
    """
    Onnx Image Text Classification Pipeline

    Args:
        model_type (str): Model type, only support ImageTextClassifier.
        save_dir (str): Model directory.
        device (str, optional): Device for inference, support cpu and gpu. Defaults to "cpu".
    """

    def __init__(
        self,
        model_type: str,
        save_dir: str,
        device: str = "cpu",
        quantization: bool = False,
        optimization: bool = False,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(os.path.join(save_dir, "text"))

        if device == "gpu":
            self.device = torch.device("cuda")
            self.image_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "image/model.onnx"),
                providers=["CUDAExecutionProvider"],
            )
            if quantization:
                self.text_ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "text/model_quantized.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            elif optimization:
                self.text_ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "text/model_optimized.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            else:
                self.text_ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "text/model.onnx"),
                    providers=["CUDAExecutionProvider"],
                )
            self.classifier_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "classifier_head.onnx"),
                providers=["CUDAExecutionProvider"],
            )
        # CPU mode
        else:
            self.device = torch.device("cpu")
            self.image_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "image/model.onnx"),
                providers=["CPUExecutionProvider"],
            )
            if quantization:
                self.text_ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "text/model_quantized.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            elif optimization:
                self.text_ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "text/model_optimized.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            else:
                self.text_ort_session = onnxruntime.InferenceSession(
                    os.path.join(save_dir, "text/model.onnx"),
                    providers=["CPUExecutionProvider"],
                )
            self.classifier_ort_session = onnxruntime.InferenceSession(
                os.path.join(save_dir, "classifier_head.onnx"),
                providers=["CPUExecutionProvider"],
            )
        # Load Train config
        with open(
            os.path.join(save_dir, "train_config.json"), "r", encoding="utf-8"
        ) as f:
            train_config = EasyDict(json.load(f))
        self.text_prompt = train_config.text_prompt
        self.label_name_list = train_config.label_name_list
        self.text_config = AutoConfig.from_pretrained(os.path.join(save_dir, "text"))

        # Load val_transforms
        with open(os.path.join(save_dir, "image", "val_transforms.pkl"), "rb") as f:
            self.transforms = pickle.load(f)

        self.classifier_head = torch.load(
            os.path.join(save_dir, "classifier_head.ckpt"), map_location=self.device
        )
        self.classifier_head.eval()

    def __call__(
        self,
        image_inputs: Union[str, List[str]],
        text_inputs: Union[str, List[str]],
        topk: int = 1,
        return_logits: bool = False,
        sigmoid: bool = False,
        only_backbone: bool = False,
        last_embedding: bool = False,
        temperature: float = 1.0,
    ):
        """
        Args:
            image_inputs (Union[str, List[str]]): Input image path or list of input image path.
            text_inputs (Union[str, List[str]]): Input text or list of input text.
            topk (int, optional): Top k prediction. Defaults to 1.
            return_logits (bool, optional): Return logits or not. Defaults to False.
            sigmoid (bool, optional): Apply sigmoid or not(Softmax). Defaults to False.
            only_backbone (bool, optional): Only return backbone output. Defaults to False.
        """
        if only_backbone and last_embedding:
            raise ValueError(
                "only_backbone and last_embedding cannot be True at the same time."
            )

        if type(image_inputs) == str:
            image_inputs = [image_inputs]

        if type(text_inputs) == str:
            text_inputs = [text_inputs]

        preprocessed_image_inputs = {
            "inputs": ImageClassifierInputPreprocess(
                image_inputs,
                device=self.device,
                transforms=self.transforms,
            )
        }

        preprocessed_text_inputs = TextClassifierInputPreprocess(
            text_inputs,
            text_prompt=self.text_prompt,
            device=self.device,
            tokenizer=self.tokenizer,
        )

        image_embeddings = onnx_inference(
            self.image_ort_session, preprocessed_image_inputs, self.device
        )
        text_embeddings = onnx_inference(
            self.text_ort_session, preprocessed_text_inputs, self.device
        )

        selected_token_embedding = TextClassifierSelectToken(
            [text_embeddings], preprocessed_text_inputs, self.text_config
        )

        embeddings = torch.cat([image_embeddings, selected_token_embedding], dim=-1)

        if only_backbone:
            return embeddings.cpu().detach().numpy()

        elif last_embedding:
            if self.classifier_head.__class__.__name__ != "Base2LinearClassifier":
                raise ValueError(
                    "last_embedding is only supported for Base2LinearClassifier."
                )
            emb = self.classifier_head.fc_layer1(embeddings.to(self.device))
            emb = self.classifier_head.bn1(emb)
            emb = F.relu(emb)
            return emb.detach().cpu().numpy()

        # CLassifier ort input preprocess
        classifier_ort_input_dict = classifier_onnx_preprocess(
            self.classifier_ort_session, embeddings
        )

        logits = onnx_inference(
            self.classifier_ort_session, classifier_ort_input_dict, self.device
        )

        return postprocess(
            logits, topk, self.label_name_list, return_logits, sigmoid, temperature
        )
