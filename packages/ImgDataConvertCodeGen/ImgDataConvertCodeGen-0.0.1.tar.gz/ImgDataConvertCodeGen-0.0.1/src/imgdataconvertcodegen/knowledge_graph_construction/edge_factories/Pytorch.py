from .type import Conversion, FactoriesCluster
from ...metadata_differ import are_both_same_data_repr, is_differ_value_for_key


def is_attribute_value_valid_for_torch(metadata):
    allowed_values = {
        "color_channel": ["rgb", "gray"],
        "channel_order": ["channel first", "channel last", "none"],
        "minibatch_input": [True, False],
        # https://pytorch.org/docs/stable/tensors.html
        # https://github.com/pytorch/vision/blob/ba64d65bc6811f2b173792a640cb4cbe5a750840/torchvision/transforms/v2/functional/_misc.py#L210-L259
        # https://pytorch.org/docs/stable/generated/torch.is_floating_point.html remove float32 full, float64 full, double full
        "image_data_type": [
            "uint8",
            "int8",
            "int16",
            "int32",
            "int64",
            "float32(0to1)",
            "float64(0to1)",
            "double(0to1)",
        ],
        "device": ["cpu", "gpu"],
    }
    for key, values in allowed_values.items():
        if key in metadata and metadata[key] not in values:
            return False
    return True


def is_metadata_valid_for_torch(metadata):
    if metadata["color_channel"] == "rgb" and metadata["channel_order"] == "none":
        return False
    return True


def can_use_factories_in_cluster(source_metadata, target_metadata):
    return (
        are_both_same_data_repr(source_metadata, target_metadata, "torch.tensor")
        and is_attribute_value_valid_for_torch(source_metadata)
        and is_attribute_value_valid_for_torch(target_metadata)
        and is_metadata_valid_for_torch(source_metadata)
        and is_metadata_valid_for_torch(target_metadata)
    )


def channel_none_to_channel_first(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "none"
        and target_metadata.get("channel_order") == "channel first"
    ):
        return "", "def convert(var):\n  return var.unsqueeze(0)"


def channel_none_to_channel_last(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "none"
        and target_metadata.get("channel_order") == "channel last"
    ):
        return "", "def convert(var):\n  return var.unsqueeze(-1)"


def channel_last_to_none(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel last"
        and target_metadata.get("channel_order") == "none"
    ):
        return "", "def convert(var):\n  return var.squeeze(-1)"


def channel_first_to_none(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel first"
        and target_metadata.get("channel_order") == "none"
    ):
        return "", "def convert(var):\n  return var.squeeze(0)"


def channel_last_to_channel_first(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel last"
        and target_metadata.get("channel_order") == "channel first"
    ):
        if source_metadata.get("minibatch_input"):
            return "", "def convert(var):\n  return var.permute(0, 3, 1, 2)"
        return "", "def convert(var):\n  return var.permute(2, 0, 1)"


def channel_first_to_channel_last(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel first"
        and target_metadata.get("channel_order") == "channel last"
    ):
        if source_metadata.get("minibatch_input"):
            return "", "def convert(var):\n  return var.permute(0, 2, 3, 1)"
        return "", "def convert(var):\n  return var.permute(1, 2, 0)"


def minibatch_true_to_false(source_metadata, target_metadata) -> Conversion:
    if source_metadata.get("minibatch_input") and not target_metadata.get(
        "minibatch_input"
    ):
        return "", "def convert(var):\n  return var.squeeze(0)"


def minibatch_false_to_true(source_metadata, target_metadata) -> Conversion:
    if (not source_metadata.get("minibatch_input")) and target_metadata.get(
        "minibatch_input"
    ):
        return "", "def convert(var):\n  return var.unsqueeze(0)"


def channel_first_rgb_to_gray(source_metadata, target_metadata) -> Conversion:
    # [N, 3, H, W] -> [N, 1, H, W]
    if (
            source_metadata.get("channel_order") == "channel first"
            and source_metadata.get("color_channel") == "rgb"
            and target_metadata.get("color_channel") == "gray"
            and source_metadata.get("minibatch_input")
    ):
        return (
            "from torchvision.transforms import functional as v1F",
            "def convert(var):\n  return v1F.rgb_to_grayscale(var)",
        )


def channel_first_gray_to_rgb(source_metadata, target_metadata) -> Conversion:
    # [N, 1, H, W] -> [N, 3, H, W]
    if (
            source_metadata.get("channel_order") == "channel first"
            and source_metadata.get("color_channel") == "gray"
            and target_metadata.get("color_channel") == "rgb"

    ):
        if source_metadata.get("minibatch_input"):
            return (
                "",
                "def convert(var):\n  return var.repeat(1, 3, 1, 1)",
            )
        else:
            return (
                "",
                "def convert(var):\n  return var.repeat(3, 1, 1)",
            )


def between_uint8_and_float32_0to1(source_metadata, target_metadata) -> Conversion:
    if source_metadata["image_data_type"] == "uint8" and target_metadata["image_data_type"] == "float32(0to1)":
        return "", "def convert(var):\n  return var / 255.0"
    elif source_metadata["image_data_type"] == "float32(0to1)" and target_metadata["image_data_type"] == "uint8":
        return "import torch", "def convert(var):\n  return (var * 255).to(torch.uint8)"


def convert_image_dtype(source_metadata, target_metadata) -> Conversion:
    # image dtype conversion involves type convert, intensity range rescale and normalization for float point
    if is_differ_value_for_key(source_metadata, target_metadata, "image_data_type"):
        # https://github.com/pytorch/vision/blob/ba64d65bc6811f2b173792a640cb4cbe5a750840/torchvision/transforms/v2/functional/_misc.py#L230-L233
        if source_metadata.get("image_data_type") == "float32(0to1)" and target_metadata.get("image_data_type") in ['int32', 'int64']:
            return None
        if source_metadata.get("image_data_type") in ["float64(0to1)", "double(0to1)"] and target_metadata.get("image_data_type") == 'int64':
            return None
        if source_metadata["image_data_type"] == "uint8" and target_metadata["image_data_type"] == "float32(0to1)":
            return None
        elif source_metadata["image_data_type"] == "float32(0to1)" and target_metadata["image_data_type"] == "uint8":
            return None
        # https://pytorch.org/docs/stable/tensors.html
        # https://github.com/pytorch/vision/blob/ba64d65bc6811f2b173792a640cb4cbe5a750840/torchvision/transforms/v2/functional/_misc.py#L210-L259
        dtype_mapping = {
            "uint8": "torch.uint8",
            "int8": "torch.int8",
            "int16": "torch.int16",
            "int32": "torch.int32",
            "int64": "torch.int64",
            "float32(0to1)": "torch.float",
            "float64(0to1)": "torch.double",
            "double(0to1)": "torch.double",
        }
        return (
            "import torch\nfrom torchvision.transforms.v2 import functional as F",
            f"def convert(var):\n return F.to_dtype(var, {dtype_mapping.get(target_metadata.get('image_data_type'))}, scale=True)",
        )


def gpu_to_cpu(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("device") == "gpu"
        and target_metadata.get("device") == "cpu"
    ):
        return "", "def convert(var):\n  return var.cpu()"


def cpu_to_gpu(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("device") == "cpu"
        and target_metadata.get("device") == "gpu"
    ):
        return "", "def convert(var):\n  return var.cuda()"


factories_cluster_for_Pytorch: FactoriesCluster = (
    can_use_factories_in_cluster,
    [
        channel_first_rgb_to_gray,
        channel_first_gray_to_rgb,
        channel_none_to_channel_first,
        channel_none_to_channel_last,
        channel_first_to_none,
        channel_first_to_channel_last,
        channel_last_to_none,
        channel_last_to_channel_first,
        minibatch_true_to_false,
        minibatch_false_to_true,
        between_uint8_and_float32_0to1,
        convert_image_dtype,
        gpu_to_cpu,
        cpu_to_gpu
    ],
)
