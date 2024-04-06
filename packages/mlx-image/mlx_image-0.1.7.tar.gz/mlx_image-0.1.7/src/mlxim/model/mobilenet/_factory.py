from typing import Any

from .._config import HFWeights, Metrics, ModelConfig, Transform
from .mobilenet import MobileNetV3, mobilenet_v3_conf

mobilenet_configs = {
    "mobilenet_v3_small": ModelConfig(
        metrics=Metrics(dataset="ImageNet-1K", accuracy_at_1=0.0, accuracy_at_5=0.0),
        transform=Transform(img_size=224),
        weights=HFWeights(repo_id="mlx-vision/mobilenet_v3_small-mlxim", filename="none.safetensors"),
    ),
    "mobilenet_v3_large": ModelConfig(
        metrics=Metrics(dataset="ImageNet-1K", accuracy_at_1=0.0, accuracy_at_5=0.0),
        transform=Transform(img_size=224),
        weights=HFWeights(repo_id="mlx-vision/mobilenet_v3_large-mlxim", filename="none.safetensors"),
    ),
}


def mobilenet_v3_large(num_classes=1000, **kwargs: Any) -> MobileNetV3:
    return MobileNetV3(num_classes=num_classes, *mobilenet_v3_conf("mobilenet_v3_large", **kwargs))


def mobilenet_v3_small(num_classes=1000, **kwargs: Any) -> MobileNetV3:
    return MobileNetV3(num_classes=num_classes, *mobilenet_v3_conf("mobilenet_v3_small", **kwargs))
