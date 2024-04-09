from .PIL import is_attribute_value_valid_for_pil, is_metadata_valid_for_pil
from .Pytorch import is_attribute_value_valid_for_torch, is_metadata_valid_for_torch
from .Tensorflow import is_attribute_value_valid_for_tensorflow, is_metadata_valid_for_tensorflow
from .numpy import is_attribute_value_valid_for_numpy, is_metadata_valid_for_numpy
from .type import Conversion, FactoriesCluster, ConversionForMetadataPair


def numpy_to_torch(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "numpy.ndarray"
            and target_metadata.get("data_representation") == "torch.tensor"
    ):
        return (
            "import torch",
            "def convert(var):\n  return torch.from_numpy(var)",
        )
    return None


def torch_to_numpy(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "torch.tensor"
            and target_metadata.get("data_representation") == "numpy.ndarray"
    ):
        return (
            "import torch",
            "def convert(var):\n  return var.numpy(force=True)",
        )
    return None


def is_convert_between_numpy_and_torch(source_metadata, target_metadata):
    # only one attribute (data representation) change, so we only check the source_metadata
    return (
            is_attribute_value_valid_for_torch(source_metadata) and
            is_attribute_value_valid_for_numpy(source_metadata) and
            is_metadata_valid_for_torch(source_metadata) and
            is_metadata_valid_for_numpy(source_metadata)
    )


factories_cluster_for_numpy_torch: FactoriesCluster = (
    is_convert_between_numpy_and_torch,
    [
        numpy_to_torch,
        torch_to_numpy,
    ]
)


def numpy_to_pil(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "numpy.ndarray"
            and target_metadata.get("data_representation") == "PIL.Image"
    ):
        return (
            "from PIL import Image",
            "def convert(var):\n  return Image.fromarray(var)",
        )
    return None


def pil_to_numpy(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "PIL.Image"
            and target_metadata.get("data_representation") == "numpy.ndarray"
    ):
        return (
            "import numpy as np",
            "def convert(var):\n  return np.array(var)",
        )
    return None


def is_convert_between_numpy_and_pil(source_metadata, target_metadata):
    # only one attribute (data representation) change, so we only check the source_metadata
    return (
            is_attribute_value_valid_for_pil(source_metadata) and
            is_attribute_value_valid_for_numpy(source_metadata) and
            is_metadata_valid_for_pil(source_metadata) and
            is_metadata_valid_for_numpy(source_metadata)
    )


factories_cluster_for_numpy_pil: FactoriesCluster = (
    is_convert_between_numpy_and_pil,
    [
        numpy_to_pil,
        pil_to_numpy,
    ]
)


def tensorflow_to_numpy(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "tf.tensor"
            and target_metadata.get("data_representation") == "numpy.ndarray"
    ):
        return "", "def convert(var):\n  return var.numpy()",
    return None


def numpy_to_tensorflow(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "numpy.ndarray"
            and target_metadata.get("data_representation") == "tf.tensor"

    ):
        return "import tensorflow as tf", f"def convert(var):\n return tf.convert_to_tensor(var)",

    return None


def is_convert_between_numpy_and_tensorflow(source_metadata, target_metadata):
    # only one attribute (data representation) change, so we only check the source_metadata
    return (
            is_attribute_value_valid_for_tensorflow(source_metadata) and
            is_attribute_value_valid_for_numpy(source_metadata) and
            is_metadata_valid_for_tensorflow(source_metadata) and
            is_metadata_valid_for_numpy(source_metadata)
    )


factories_cluster_for_numpy_tensorflow: FactoriesCluster = (
    is_convert_between_numpy_and_tensorflow,
    [
        numpy_to_tensorflow,
        tensorflow_to_numpy,
    ]
)


def pil_to_tensorflow(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("data_representation") == "PIL.Image"
            and target_metadata.get("data_representation") == "tf.tensor"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.convert_to_tensor(var)",
        )
    return None


def is_convert_between_pil_and_tensorflow(source_metadata, target_metadata):
    # only one attribute (data representation) change, so we only check the source_metadata
    return (
            is_attribute_value_valid_for_tensorflow(source_metadata) and
            is_attribute_value_valid_for_pil(source_metadata) and
            is_metadata_valid_for_tensorflow(source_metadata) and
            is_metadata_valid_for_pil(source_metadata)
    )


factories_cluster_for_pil_tensorflow: FactoriesCluster = (
    is_convert_between_pil_and_tensorflow,
    [
        pil_to_tensorflow,

    ]
)

# https://pytorch.org/vision/master/generated/torchvision.transforms.ToPILImage.html#torchvision.transforms.ToPILImage
# Converts a torch.*Tensor of shape C x H x W to a PIL Image while adjusting the value range depending on the mode.
torch_to_pil = ("from torchvision.transforms import functional as F", "def convert(var):\n  return F.to_pil_image(var)")

factories_for_pil_torch_metadata_pair: list[ConversionForMetadataPair] = [
    # torch tensor, channel first, rgb, float32(0to1) -> PIL image, chanel last, uint8, rgb
    (
        {
            "data_representation": "torch.tensor",
            "color_channel": 'rgb',
            "channel_order": 'channel first',
            "minibatch_input": False,
            "image_data_type": 'float32(0to1)',
            "device": 'cpu',
        },
        {
            "data_representation": "PIL.Image",
            "color_channel": "rgb",
            "channel_order": 'channel last',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        },
        torch_to_pil
    ),
    # torch tensor, channel first, grayscale, float32(0to1) -> PIL image, chanel last, uint8, rgb or grayscale
    (
        {
            "data_representation": "torch.tensor",
            "color_channel": 'gray',
            "channel_order": 'channel first',
            "minibatch_input": False,
            "image_data_type": 'float32(0to1)',
            "device": 'cpu',
        },
        {
            "data_representation": "PIL.Image",
            "color_channel": 'gray',
            "channel_order": 'none',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        },
        torch_to_pil
    )
]

# https://pytorch.org/vision/master/generated/torchvision.transforms.ToTensor.html
# Converts a PIL Image to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0]
# if the PIL Image belongs to one of the modes (L, LA, P, I, F, RGB, YCbCr, RGBA, CMYK, 1)
for color_channel in ["rgb", "gray"]:
    factories_for_pil_torch_metadata_pair.append(
        #  PIL image, chanel last, uint8 -> torch tensor, channel first, float32(0to1)
        (
            {
                "data_representation": "PIL.Image",
                "color_channel": color_channel,
                "channel_order": 'channel last',
                "minibatch_input": False,
                "image_data_type": 'uint8',
                "device": 'cpu',
            },
            {
                "data_representation": "torch.tensor",
                "color_channel": color_channel,
                "channel_order": 'channel first',
                "minibatch_input": False,
                "image_data_type": 'float32(0to1)',
                "device": 'cpu',
            },
            ("from torchvision.transforms import functional as F", "def convert(var):\n  return F.to_tensor(var)")
        )
    )
