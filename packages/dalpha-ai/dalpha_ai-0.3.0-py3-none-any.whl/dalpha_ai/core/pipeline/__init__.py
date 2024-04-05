# from .pipeline import pipeline
import torch
import os
from .onnx_pipeline import (
    OnnxTextClassificationPipeline,
    OnnxImageClassificationPipeline,
    OnnxImageTextClassificationPipeline,
)
from .pytorch_pipeline import PytorchClassificationPipeline

# Register all supported pipeline for each model type.
MODEL_TYPE_PIPELINES = {
    "TextClassifier": {
        "pytorch": PytorchClassificationPipeline,
        "onnx": OnnxTextClassificationPipeline,
    },
    "ImageClassifier": {
        "pytorch": PytorchClassificationPipeline,
        "onnx": OnnxImageClassificationPipeline,
    },
    "ImageTextClassifier": {
        "pytorch": PytorchClassificationPipeline,
        "onnx": OnnxImageTextClassificationPipeline,
    },
}


def pipeline(
    model_type: str,
    save_dir: str,
    inference_engine: str = "onnx",
    device: str = "cpu",
    quantization: bool = False,
    optimization: bool = False,
):
    """
    Initialize pipeline for inference, support both onnx and pytorch inference engine.
    Each model type will have different pipeline, for example:
        - TextClassifier: OnnxTextClassificationPipeline, PytorchClassificationPipeline

    Args:
        model_type (str): Model type, support TextClassifier, ImageClassifier, ImageTextClassifier.
        save_dir (str): Model directory.
        inference_engine (str, optional): Inference engine, support onnx and pytorch. Defaults to "onnx".
        device (str, optional): Device for inference, support cpu and gpu. Defaults to "cpu".
    """
    assert os.path.isdir(save_dir), f"Not existing model directory {save_dir}"

    # Only support onnx and pytorch inference engine.
    if inference_engine not in ["onnx", "pytorch"]:
        raise ValueError(f"Not supported inference engine: {inference_engine}")

    if model_type not in MODEL_TYPE_PIPELINES.keys():
        raise ValueError(f"Not supported model type: {model_type}")

    pipeline_class = MODEL_TYPE_PIPELINES[model_type][inference_engine]

    return pipeline_class(model_type, save_dir, device, quantization, optimization)
