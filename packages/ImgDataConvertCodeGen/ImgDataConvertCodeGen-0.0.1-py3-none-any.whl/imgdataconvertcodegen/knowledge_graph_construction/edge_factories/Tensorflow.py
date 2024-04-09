from .type import Conversion, FactoriesCluster
from ...metadata_differ import are_both_same_data_repr, is_differ_value_for_key


def is_attribute_value_valid_for_tensorflow(metadata):
    allowed_values = {
        "color_channel": ["rgb", "gray"],
        "channel_order": ["channel first", "channel last", "none"],
        "minibatch_input": [True, False],
        # https://www.tensorflow.org/api_docs/python/tf/dtypes
        # https://www.tensorflow.org/api_docs/python/tf/image/convert_image_dtype
        "image_data_type": [
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "int8",
            "int16",
            "int32",
            "int64",
            "float16(0to1)",
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


def is_metadata_valid_for_tensorflow(metadata):
    if metadata["color_channel"] == "rgb" and metadata["channel_order"] == "none":
        return False
    return True


def can_use_factories_in_cluster(source_metadata, target_metadata):
    return (
        are_both_same_data_repr(source_metadata, target_metadata, "tf.tensor")
        and is_attribute_value_valid_for_tensorflow(source_metadata)
        and is_attribute_value_valid_for_tensorflow(target_metadata)
        and is_metadata_valid_for_tensorflow(source_metadata)
        and is_metadata_valid_for_tensorflow(target_metadata)
    )


def minibatch_true_to_false(source_metadata, target_metadata) -> Conversion:
    if source_metadata.get("minibatch_input") and not target_metadata.get(
        "minibatch_input"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.squeeze(var, 0)",
        )


def minibatch_false_to_true(source_metadata, target_metadata) -> Conversion:
    if (not source_metadata.get("minibatch_input")) and target_metadata.get(
        "minibatch_input"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.expand_dims(var, 0)",
        )


def channel_none_to_channel_first(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "none"
        and target_metadata.get("channel_order") == "channel first"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.expand_dims(var, 0)",
        )


def channel_none_to_channel_last(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "none"
        and target_metadata.get("channel_order") == "channel last"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.expand_dims(var, -1)",
        )


def channel_last_to_none(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel last"
        and target_metadata.get("channel_order") == "none"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.squeeze(var, -1)",
        )


def channel_first_to_none(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel first"
        and target_metadata.get("channel_order") == "none"
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.squeeze(var, 0)",
        )


def channel_last_to_channel_first(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel last"
        and target_metadata.get("channel_order") == "channel first"
    ):
        if source_metadata.get("minibatch_input"):
            return (
                "import tensorflow as tf",
                "def convert(var):\n  return tf.transpose(var, [0, 3, 1, 2])",
            )
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.transpose(var, [2, 0, 1])",
        )


def channel_first_to_channel_last(source_metadata, target_metadata) -> Conversion:
    if (
        source_metadata.get("channel_order") == "channel first"
        and target_metadata.get("channel_order") == "channel last"
    ):
        if source_metadata.get("minibatch_input"):
            return (
                "import tensorflow as tf",
                "def convert(var):\n  return tf.transpose(var, [0, 2, 3, 1])",
            )
        return (
            "import tensorflow as tf",
            "def convert(var):\n   return tf.transpose(var, [1, 2, 0])",
        )


def channel_last_rgb_to_gray(source_metadata, target_metadata) -> Conversion:
    # [N, H, W, 3] -> [N, H, W, 1]
    if (
        source_metadata.get("channel_order") == "channel last"
        and source_metadata.get("color_channel") == "rgb"
        and target_metadata.get("color_channel") == "gray"
        and source_metadata.get("minibatch_input")
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.image.rgb_to_grayscale(var)",
        )


def channel_last_gray_to_rgb(source_metadata, target_metadata) -> Conversion:
    # [N, H, W, 1] -> [N, H, W, 3]
    # Outputs a tensor of the same `DType`
    if (
        source_metadata.get("channel_order") == "channel last"
        and source_metadata.get("color_channel") == "gray"
        and target_metadata.get("color_channel") == "rgb"
        # tensorflow/core/framework/local_rendezvous.cc:404] Local rendezvous is aborting with status: UNIMPLEMENTED: TileOp : The input data type is not supported, DataType : uint16, Dimension : 4
        and source_metadata.get("image_data_type") != "uint16"
        and source_metadata.get("minibatch_input")
    ):
        return (
            "import tensorflow as tf",
            "def convert(var):\n  return tf.image.grayscale_to_rgb(var)",
        )


def convert_image_dtype(source_metadata, target_metadata) -> Conversion:
    if is_differ_value_for_key(source_metadata, target_metadata, "image_data_type"):
        # https://www.tensorflow.org/api_docs/python/tf/dtypes
        # https://www.tensorflow.org/api_docs/python/tf/image/convert_image_dtype
        dtype_mapping = {
            "uint8": "tf.uint8",
            "uint16": "tf.uint16",
            "uint32": "tf.uint32",
            "uint64": "tf.uint64",
            "int8": "tf.int8",
            "int16": "tf.int16",
            "int32": "tf.int32",
            "int64": "tf.int64",
            "float16(0to1)": "tf.float16",
            "float32(0to1)": "tf.float32",
            "float64(0to1)": "tf.float64",
            "double(0to1)": "tf.float64",
        }
        target_dtype = dtype_mapping.get(target_metadata.get("image_data_type"))
        return (
            "import tensorflow as tf",
            f"def convert(var):\n return tf.image.convert_image_dtype(var, {target_dtype})",
        )


def gpu_to_cpu(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("device") == "gpu"
            and target_metadata.get("device") == "cpu"
    ):
        return (
            "import tensorflow as tf",
            """def convert(var):
    with tf.device('/cpu:0'):
        return tf.identity(var)""",
        )


def cpu_to_gpu(source_metadata, target_metadata) -> Conversion:
    if (
            source_metadata.get("device") == "cpu"
            and target_metadata.get("device") == "gpu"
    ):
        return (
            "import tensorflow as tf",
            """def convert(var):
    with tf.device('/device:GPU:0'):
        return tf.identity(var)""",
        )
    return None


factories_cluster_for_tensorflow: FactoriesCluster = (
    can_use_factories_in_cluster,
    [
        channel_last_rgb_to_gray,
        channel_last_gray_to_rgb,
        channel_none_to_channel_first,
        channel_none_to_channel_last,
        channel_first_to_none,
        channel_first_to_channel_last,
        channel_last_to_none,
        channel_last_to_channel_first,
        minibatch_true_to_false,
        minibatch_false_to_true,
        convert_image_dtype,
        gpu_to_cpu,
        cpu_to_gpu,
    ],
)
