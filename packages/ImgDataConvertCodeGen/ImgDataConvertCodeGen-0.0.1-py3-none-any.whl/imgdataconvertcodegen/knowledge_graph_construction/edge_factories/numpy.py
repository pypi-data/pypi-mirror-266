from .type import Conversion, FactoriesCluster
from ...metadata_differ import are_both_same_data_repr, is_differ_value_for_key


def is_metadata_valid_for_numpy(metadata):
    if metadata["color_channel"] in ["rgb", "bgr"] and metadata["channel_order"] == "none":
        return False
    return True


def is_attribute_value_valid_for_numpy(metadata):
    allowed_values = {
        "color_channel": ["rgb", "bgr", "gray"],
        "channel_order": ["channel first", "channel last", "none"],
        # https://numpy.org/doc/stable/user/basics.types.html
        # https://scikit-image.org/docs/stable/user_guide/data_types.html
        "minibatch_input": [True, False],
        "image_data_type": [
            "uint8",
            "uint16",
            "uint32",
            "int8",
            "int16",
            "int32",
            "float32(0to1)",
            "float32(-1to1)",
            "float64(0to1)",
            "float64(-1to1)",
            "double(0to1)",
            "double(-1to1)",
        ],
        "device": ["cpu"],
    }
    for key, values in allowed_values.items():
        if key in metadata and metadata[key] not in values:
            return False
    return True


def can_use_factories_in_cluster(source_metadata, target_metadata):
    return (
            are_both_same_data_repr(source_metadata, target_metadata, "numpy.ndarray")
            and is_attribute_value_valid_for_numpy(source_metadata)
            and is_attribute_value_valid_for_numpy(target_metadata)
            and is_metadata_valid_for_numpy(source_metadata)
            and is_metadata_valid_for_numpy(target_metadata)
    )


def channel_first_between_bgr_rgb(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel first":
        return None
    if ((source_metadata["color_channel"] == "bgr" and target_metadata["color_channel"] == "rgb") or
            (source_metadata["color_channel"] == "rgb" and target_metadata["color_channel"] == "bgr")):
        if source_metadata["minibatch_input"]:
            # [N, C, H, W]
            return "import numpy as np", "def convert(var):\n  return var[:, ::-1, :, :]"
        # [C, H, W]
        return "import numpy as np", "def convert(var):\n  return var[::-1, :, :]"


def channel_first_rgb_to_gray(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel first":
        return None
    if (
            source_metadata["color_channel"] == "rgb"
            and target_metadata["color_channel"] == "gray"
    ):
        if source_metadata["minibatch_input"]:
            # [N, 3, H, W] -> [N, 1, H, W]
            return (
                "import numpy as np",
                """def convert(var):
    type_in = var.dtype
    weights = np.array([0.299, 0.587, 0.114]).reshape((1, 3, 1, 1))
    var = np.sum(var * weights, axis=1, keepdims=True)
    return var.astype(type_in)""")
        # [3, H, W] -> [1, H, W]
        return (
            "import numpy as np",
            """def convert(var):
    type_in = var.dtype
    var = np.sum(var * np.array([0.299, 0.587, 0.114]).reshape(3, 1, 1), axis=0, keepdims=True)
    return var.astype(type_in)""")


def channel_first_bgr_to_gray(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel first":
        return None
    if (
            source_metadata["color_channel"] == "bgr"
            and target_metadata["color_channel"] == "gray"
    ):
        if source_metadata["minibatch_input"]:
            # [N, 3, H, W] -> [N, 1, H, W]
            return (
                "import numpy as np",
                """def convert(var):
    type_in = var.dtype
    weights = np.array([0.114, 0.587, 0.299]).reshape((1, 3, 1, 1))
    var = np.sum(var * weights, axis=1, keepdims=True)
    return var.astype(type_in)""")
        # [3, H, W] -> [1, H, W]
        return (
            "import numpy as np",
            """def convert(var):
    type_in = var.dtype
    var = np.sum(var * np.array([0.114, 0.587, 0.299]).reshape(3, 1, 1), axis=0)
    return var.astype(type_in)""")


def channel_first_gray_to_rgb_or_bgr(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel first":
        return None
    if (
            source_metadata["color_channel"] == "gray"
            and target_metadata["color_channel"] != "gray"
    ):
        if source_metadata["minibatch_input"]:
            # [N, 1, H, W] -> [N, 3, H, W]
            return (
                "import numpy as np",
                "def convert(var):\n  return np.repeat(var, 3, axis=1)",
            )
        # [1, H, W] -> [3, H, W]
        return (
            "import numpy as np",
            "def convert(var):\n  return np.repeat(var, 3, axis=0)",
        )


def channel_last_between_bgr_rgb(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel last":
        return None
    if ((source_metadata["color_channel"] == "bgr" and target_metadata["color_channel"] == "rgb")
            or (source_metadata["color_channel"] == "rgb" and target_metadata["color_channel"] == "bgr")):
        if source_metadata["minibatch_input"]:
            # [N, H, W, C]
            return (
                "import numpy as np",
                "def convert(var):\n  return var[:, :, :, ::-1]",
            )
        # [H, W, C]
        return "import numpy as np", "def convert(var):\n  return var[:, :, ::-1]"


def channel_last_rgb_to_gray(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel last":
        return None
    if source_metadata["color_channel"] == "rgb" and target_metadata["color_channel"] == "gray":
        if source_metadata["minibatch_input"]:
            # [N, H, W, 3] -> [N, H, W, 1]
            return (
                "import numpy as np",
                """def convert(var):
    type_in = var.dtype
    var = np.expand_dims(np.dot(var[..., :3], [0.299, 0.587, 0.114]), axis=-1)
    return var.astype(type_in)""")
        # [H, W, 3] -> [H, W, 1]
        return (
            "import numpy as np",
            """def convert(var):
    type_in = var.dtype
    var = np.expand_dims(np.dot(var, [0.299, 0.587, 0.114]), axis=-1)
    return var.astype(type_in)""")


def channel_last_bgr_to_gray(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel last":
        return None
    if source_metadata["color_channel"] == "bgr" and target_metadata["color_channel"] == "gray":
        # [N, H, W, 3] -> [N, H, W, 1] or [H, W, 3] -> [H, W, 1]
        return (
            "import numpy as np",
            """def convert(var):
    type_in = var.dtype
    var = np.expand_dims(np.dot(var[..., :3], [0.114, 0.587, 0.299]), axis=-1)
    return var.astype(type_in)""")


def channel_last_gray_to_rgb_or_gbr(source_metadata, target_metadata) -> Conversion:
    if source_metadata["channel_order"] != "channel last":
        return None
    if (
            source_metadata["color_channel"] == "gray"
            and target_metadata["color_channel"] != "gray"
    ):
        if source_metadata["minibatch_input"]:
            # [N, H, W, 1] -> [N, H, W, 3]
            return (
                "import numpy as np",
                "def convert(var):\n  return np.repeat(var, 3, axis=-1)",
            )
        # [H, W, 1] -> [H, W, 3]
        return (
            "import numpy as np",
            "def convert(var):\n  return np.repeat(var, 3, axis=2)",
        )


def channel_last_to_channel_first(source_metadata, target_metadata) -> Conversion:
    if source_metadata['channel_order'] == 'channel last' and target_metadata['channel_order'] == 'channel first':
        if source_metadata['minibatch_input']:
            # [N, H, W, C] -> [N, C, H, W]
            return "", "def convert(var):\n  return var.transpose(0, 3, 1, 2)"
        # [H, W, C] -> [C, H, W]
        return "", "def convert(var):\n  return var.transpose(2, 0, 1)"


def channel_last_to_channel_none(source_metadata, target_metadata) -> Conversion:
    # only one attribute change and when channel_order is none, the color channel must be gray, so we don't need to
    # check color channel
    if source_metadata['channel_order'] == 'channel last' and target_metadata['channel_order'] == 'none':
        # [N, H, W, 1] -> [N, H, W] or [H, W, 1] -> [H, W]
        return "", "def convert(var):\n  return var.squeeze(-1)"


def channel_first_to_channel_last(source_metadata, target_metadata) -> Conversion:
    if source_metadata['channel_order'] == 'channel first' and target_metadata['channel_order'] == 'channel last':
        if source_metadata['minibatch_input']:
            # [N, C, H, W] -> [N, H, W, C]
            return "", "def convert(var):\n  return var.transpose(0, 2, 3, 1)"
        # [C, H, W] -> [H, W, C]
        return "", "def convert(var):\n  return var.transpose(1, 2, 0)"


def channel_first_to_channel_none(source_metadata, target_metadata) -> Conversion:
    if source_metadata['channel_order'] == 'channel first' and target_metadata['channel_order'] == 'none':
        if source_metadata['minibatch_input']:
            # [N, 1, H, W] -> [N, H, W]
            return "", "def convert(var):\n  return var.squeeze(1)"
        # [1, H, W] -> [H, W]
        return "", "def convert(var):\n  return var.squeeze(0)"


def channel_none_to_channel_first(source_metadata, target_metadata) -> Conversion:
    if source_metadata['channel_order'] == 'none' and target_metadata['channel_order'] == 'channel first':
        if source_metadata['minibatch_input']:
            # [N, H, W] -> [N, 1, H, W]
            return "import numpy as np", "def convert(var):\n  return np.expand_dims(var, axis=1)"
        # [H, W] -> [1, H, W]
        return "import numpy as np", "def convert(var):\n  return np.expand_dims(var, axis=0)"


def channel_none_to_channel_last(source_metadata, target_metadata) -> Conversion:
    if source_metadata['channel_order'] == 'none' and target_metadata['channel_order'] == 'channel last':
        # [N, H, W] -> [N, H, W, 1] or [H, W] -> [H, W, 1]
        return "import numpy as np", "def convert(var):\n  return np.expand_dims(var, axis=-1)"


def minibatch_true_to_false(source_metadata, target_metadata) -> Conversion:
    if source_metadata['minibatch_input'] and not target_metadata['minibatch_input']:
        return "", "def convert(var):\n  return var[0]"


def minibatch_false_to_true(source_metadata, target_metadata) -> Conversion:
    if not source_metadata['minibatch_input'] and target_metadata['minibatch_input']:
        return "import numpy as np", "def convert(var):\n  return var[np.newaxis, ...]"


# https://numpy.org/doc/stable/user/basics.types.html
# https://scikit-image.org/docs/stable/user_guide/data_types.html
dtype_mapping = {
    "uint8": "np.uint8",
    "uint16": "np.uint16",
    "uint32": "np.uint32",
    "int8": "np.int8",
    "int16": "np.int16",
    "int32": "np.int32",
}


def image_data_to_uint8_full_range(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["uint16", "uint32", "int8", "int16", "int32",
                                                       "float32(0to1)", "float64(0to1)", "double(0to1)"]
            and target_metadata.get("image_data_type") == "uint8"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_ubyte(var)",


def image_data_to_uint16_full_range(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["uint8", "uint32", "int8", "int16", "int32",
                                                       "float32(0to1)", "float64(0to1)", "double(0to1)"]
            and target_metadata.get("image_data_type") == "uint16"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_uint(var)",


def image_data_to_int16_full_range(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["uint8", "uint16", "uint32", "int8", "int32",
                                                       "float32(-1to1)", "float64(-1to1)", "double(-1to1)",
                                                       "float32(0to1)", "float64(0to1)", "double(0to1)"]
            and target_metadata.get("image_data_type") == "int16"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_int(var)",


dtype_float_mapping = {
    "float32": "np.float32",
    "float64": "np.float64",
    "double": "np.float64",
}

dtype_float_0_to_1_mapping = {
    "float32(0to1)": "np.float32",
    "float64(0to1)": "np.float64",
    "double(0to1)": "np.float64",
}

dtype_float_minus1_to_1_mapping = {
    "float32(-1to1)": "np.float32",
    "float64(-1to1)": "np.float64",
    "double(-1to1)": "np.float64",
}


def convert_image_dtype_float_to_float(source_metadata, target_metadata) -> Conversion:
    if is_differ_value_for_key(source_metadata, target_metadata, "image_data_type"):
        for float_type_mapping in [dtype_float_mapping, dtype_float_0_to_1_mapping, dtype_float_minus1_to_1_mapping]:
            if source_metadata["image_data_type"] in float_type_mapping and target_metadata["image_data_type"] in float_type_mapping:
                return (
                    "import numpy as np",
                    f"def convert(var):\n return var.astype({float_type_mapping[target_metadata['image_data_type']]})",
                )


def image_data_unsigned_integer_to_float32_0_to_1(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["uint8", "uint16", "uint32"]
            and target_metadata.get("image_data_type") == "float32(0to1)"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_float32(var)",


def image_data_float32_minus1_1_to_float32_0_1(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") == "float32(-1to1)"
            and target_metadata.get("image_data_type") == "float32(0to1)"
    ):
        return "", "def convert(var):\n return var * 0.5 + 0.5"


def image_data_integer_to_float32_minus1_to_1(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["int8", "int16", "int32"]
            and target_metadata.get("image_data_type") == "float32(-1to1)"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_float32(var)",


def image_data_float32_0_1_to_float32_minus1_1(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") == "float32(0to1)"
            and target_metadata.get("image_data_type") == "float32(-1to1)"
    ):
        return "", "def convert(var):\n return var * 2.0 - 1"


def image_data_integer_to_float64_minus1_to_1(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["int8", "int16", "int32"]
            and target_metadata.get("image_data_type") == "float64(-1to1)"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_float64(var)",


def image_data_unsigned_integer_to_float64_0_to_1(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("image_data_type") in ["uint8", "uint16", "uint32"]
            and target_metadata.get("image_data_type") == "float64(0to1)"
    ):
        return "import skimage as ski", "def convert(var):\n return ski.util.img_as_float64(var)",


factories_cluster_for_numpy: FactoriesCluster = (
    can_use_factories_in_cluster,
    [
        channel_first_between_bgr_rgb,
        channel_first_rgb_to_gray,
        channel_first_bgr_to_gray,
        channel_first_gray_to_rgb_or_bgr,
        channel_last_between_bgr_rgb,
        channel_last_rgb_to_gray,
        channel_last_bgr_to_gray,
        channel_last_gray_to_rgb_or_gbr,
        channel_last_to_channel_first,
        channel_last_to_channel_none,
        channel_first_to_channel_last,
        channel_first_to_channel_none,
        channel_none_to_channel_first,
        channel_none_to_channel_last,
        minibatch_true_to_false,
        minibatch_false_to_true,
        image_data_to_uint8_full_range,
        image_data_to_uint16_full_range,
        image_data_to_int16_full_range,
        convert_image_dtype_float_to_float,
        image_data_unsigned_integer_to_float32_0_to_1,
        image_data_integer_to_float32_minus1_to_1,
        image_data_float32_minus1_1_to_float32_0_1,
        image_data_unsigned_integer_to_float64_0_to_1,
        image_data_integer_to_float64_minus1_to_1,
        image_data_float32_0_1_to_float32_minus1_1
    ],
)
