"""
In the knowledge graph, the node is metadata description with some attributes for image data.
Some of the nodes are end nodes, which used to represent the image data in the specific libraries
while some of the nodes are intermediate nodes, which used to represent the intermediate data representation.
Typing the concrete metadata needs the effort to know exact value for each attribute. We introduce the metadata-mapper
to help user to get the metadata description for the image data in the specific library. Some function also supports
multiple format image data as the input.
"""

from typing import TypedDict, Literal, Optional


class ImageDesc(TypedDict, total=False):
    lib: str
    color_channel: Optional[Literal['gray', 'rgb', 'bgr', 'rgba', 'graya']]
    image_dtype: Optional[Literal[
        'uint8', 'uint16', 'uint32', 'uint64',
        'int8', 'int16', 'int32', 'int64',
        'float32(0to1)', 'float32(-1to1)',
        'float64(0to1)', 'float64(-1to1)',
        'double(0to1)', 'double(-1to1)'
    ]]
    device: Optional[Literal['cpu', 'gpu']]


def end_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc):
    mapper = {
        "numpy": numpy_metadata_mapper,
        "scikit-image": scikit_img_metadata_mapper,
        "opencv": opencv_metadata_mapper,
        "PIL": pillow_metadata_mapper,
        "scipy": scipy_metadata_mapper,
        "torch": torch_metadata_mapper,
        "kornia": kornia_metadata_mapper,
        "tensorflow": tensorflow_metadata_mapper,
        "matplotlib": matplotlib_imshow_metadata_mapper
    }
    if from_image_desc["lib"] not in mapper:
        raise ValueError(f"Unsupported library: {from_image_desc['lib']}. Supported libraries are {mapper.keys()}")
    if to_image_desc["lib"] not in mapper:
        raise ValueError(f"Unsupported library: {to_image_desc['lib']}. Supported libraries are {mapper.keys()}")

    from_metadata = mapper[from_image_desc["lib"]](from_image_desc)
    to_metadata = mapper[to_image_desc["lib"]](from_image_desc, to_image_desc, False)
    return from_metadata, to_metadata


def numpy_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                          return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for numpy.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "uint8"
    supported_image_dtype = [
        'uint8', 'uint16', 'uint32',
        'int8', 'int16', 'int32',
        'float32(0to1)', 'float32(-1to1)',
        'float64(0to1)', 'float64(-1to1)',
        'double(0to1)', 'double(-1to1)',
    ]
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for numpy.")

    return {
        "data_representation": "numpy.ndarray",
        "color_channel": color_channel,
        "channel_order": "channel last" if color_channel != "gray" else "none",
        "minibatch_input": False,
        "image_data_type": image_dtype,
        "device": "cpu"
    }


def scikit_img_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                               return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    if color_channel not in ["rgb", "gray"]:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are 'rgb' and 'gray' for scikit-image.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "uint8"
    supported_image_dtype = [
        'uint8', 'uint16', 'uint32',
        "float32(0to1)", "float64(0to1)", "double(0to1)",
        "float32(-1to1)", "float64(-1to1)", "double(-1to1)",
        'int8', 'int16', 'int32'
    ]
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for scikit-image.")

    return {
        "data_representation": "numpy.ndarray",
        "color_channel": color_channel,
        "channel_order": "channel last" if color_channel != "gray" else "none",
        "minibatch_input": False,
        "image_data_type": image_dtype,
        "device": "cpu"
    }


def opencv_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                           return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "bgr"
    if color_channel not in ["bgr", "gray"]:
        raise ValueError(f"Unsupported color channel: {color_channel}, "
                         f"Supported color channels are 'bgr' and 'gray for opencv-python.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "uint8"
    supported_image_dtype = ['uint8']
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for opencv-python.")

    return {
        "data_representation": "numpy.ndarray",
        "color_channel": color_channel,
        "channel_order": "channel last" if color_channel != "gray" else "none",
        "minibatch_input": False,
        "image_data_type": image_dtype,
        "device": "cpu"
    }


def pillow_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                           return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray", "rgba", "graya"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for PIL.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "uint8"
    supported_image_dtype = ['uint8']
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for PIL.")

    return {
        "data_representation": "PIL.Image",
        "color_channel": color_channel,
        "channel_order": "channel last" if color_channel != "gray" else "none",
        "minibatch_input": False,
        "image_data_type": image_dtype,
        "device": "cpu"
    }


def scipy_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                          return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for scipy.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "uint8"
    supported_image_dtype = ['uint8', 'uint16', 'float32(0to1)', 'int8', 'int16', "int32"]
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for scipy.")

    return {
        "data_representation": "numpy.ndarray",
        "color_channel": color_channel,
        "channel_order": "channel last" if color_channel != "gray" else "none",
        "minibatch_input": False,
        "image_data_type": image_dtype,
        "device": "cpu"
    }


def matplotlib_imshow_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                                      return_from_image_metadata=False):
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html
    if return_from_image_metadata:
        raise ValueError("matplotlib is not supported as input image data representation.")
    from_lib = from_image_desc["lib"]
    which_image = to_image_desc

    if from_lib not in ["PIL", "numpy"]:
        raise ValueError(f"Unsupported library: {from_lib}. Supported libraries are ['PIL', 'numpy'] "
                         f"as the input of matplotlib.pyplot.imshow")

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray", "rgba"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for matplotlib.")

    # find the closed metadata for the input image
    if from_lib == "numpy":
        image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "uint8"
        supported_image_dtype = ['uint8', 'float32(0to1)', 'float64(0to1)']
        if image_dtype not in supported_image_dtype:
            raise ValueError(f"Unsupported image data type: {image_dtype}. "
                             f"Supported image data types are {supported_image_dtype} for matplotlib.")
        return {
            "data_representation": "numpy.ndarray",
            "color_channel": color_channel,
            "channel_order": "channel last" if color_channel != "gray" else "none",
            "minibatch_input": False,
            "image_data_type": image_dtype,
            "device": "cpu"
        }
    else:
        return {
            "data_representation": "PIL.Image",
            "color_channel": color_channel,
            "channel_order": "channel last" if color_channel != "gray" else "none",
            "minibatch_input": False,
            "image_data_type": "uint8",
            "device": "cpu"
        }


def torch_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                          return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for pytorch.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "float32(0to1)"
    supported_image_dtype = [
        "uint8",
        "int8",
        "int16",
        "int32",
        "int64",
        "float32(0to1)",
        "float64(0to1)",
        "double(0to1)",
    ]
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for pytorch.")

    supported_device = ['cpu', 'gpu']
    device = which_image["device"] if "device" in which_image else "cpu"
    if device not in supported_device:
        raise ValueError(f"Unsupported device: {device}. Supported devices are {supported_device} for pytorch.")

    return {
        "data_representation": "torch.tensor",
        "color_channel": color_channel,
        "channel_order": "channel first",
        "minibatch_input": True,
        "image_data_type": image_dtype,
        "device": device
    }


def kornia_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                           return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for kornia.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "float32(0to1)"
    supported_image_dtype = ['float32(0to1)']
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for kornia.")

    supported_device = ['cpu', 'gpu']
    device = which_image["device"] if "device" in which_image else "cpu"
    if device not in supported_device:
        raise ValueError(f"Unsupported device: {device}. Supported devices are {supported_device} for kornia.")

    return {
        "data_representation": "torch.tensor",
        "color_channel": color_channel,
        "channel_order": "channel first",
        "minibatch_input": True,
        "image_data_type": image_dtype,
        "device": device
    }


def tensorflow_metadata_mapper(from_image_desc: ImageDesc, to_image_desc: ImageDesc = None,
                               return_from_image_metadata=True):
    which_image = from_image_desc if return_from_image_metadata else to_image_desc

    color_channel = which_image["color_channel"] if "color_channel" in which_image else "rgb"
    supported_color_channels = ["rgb", "gray"]
    if color_channel not in supported_color_channels:
        raise ValueError(f"Unsupported color channel: {color_channel}. "
                         f"Supported color channels are {supported_color_channels} for tensorflow.")

    image_dtype = which_image["image_dtype"] if "image_dtype" in which_image else "float32(0to1)"
    supported_image_dtype = [
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
    ]
    if image_dtype not in supported_image_dtype:
        raise ValueError(f"Unsupported image data type: {image_dtype}. "
                         f"Supported image data types are {supported_image_dtype} for tensorflow.")

    supported_device = ['cpu', 'gpu']
    device = which_image["device"] if "device" in which_image else "cpu"
    if device not in supported_device:
        raise ValueError(f"Unsupported device: {device}. Supported devices are {supported_device} for tensorflow.")

    return {
        "data_representation": "tf.tensor",
        "color_channel": color_channel,
        "channel_order": "channel last",
        "minibatch_input": True,
        "image_data_type": image_dtype,
        "device": device
    }
