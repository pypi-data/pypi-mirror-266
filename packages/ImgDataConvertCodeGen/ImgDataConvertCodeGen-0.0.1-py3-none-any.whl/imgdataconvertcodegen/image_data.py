import numpy as np
import skimage as ski
import tensorflow as tf
import torch
from PIL import Image
from torchvision.transforms import functional as V1F
from torchvision.transforms.v2 import functional as V2F

h, w = 20, 20


def set_image_dim(new_w, new_h):
    global w, h
    w = new_w
    h = new_h


def get_r_g_b():
    r = np.random.randint(0, 256, size=(h, w), dtype=np.uint8)
    g = np.random.randint(0, 256, size=(h, w), dtype=np.uint8)
    b = np.random.randint(0, 256, size=(h, w), dtype=np.uint8)
    return r, g, b

def get_input_image_and_expected_output(source_metadata, target_metadata):
    if source_metadata["data_representation"] == target_metadata["data_representation"]:
        return get_test_images(source_metadata, target_metadata)
    else:
        src_img = get_test_images(source_metadata)[0]
        return src_img, convert_to_another_repr(source_metadata, src_img, target_metadata)


def convert_to_another_repr(source_metadata, src_img, target_metadata):
    mapping = {
        "numpy.ndarray":
            {
                "torch.tensor": lambda x: torch.from_numpy(x),
                "tf.tensor": lambda x: tf.convert_to_tensor(x),
                "PIL.Image": lambda x: Image.fromarray(x),
            },
        "PIL.Image":
            {
                "numpy.ndarray": lambda x: np.array(x),
                "torch.tensor": lambda x: V1F.to_tensor(x),
                "tf.tensor": lambda x: tf.convert_to_tensor(x),  # to check?
            },
        "torch.tensor":
            {
                "numpy.ndarray": lambda x: x.numpy(),
                "PIL.Image": lambda x: V1F.to_pil_image(x),
            },
        "tf.tensor":
            {
                "numpy.ndarray": lambda x: x.numpy(),
                "PIL.Image": lambda x: V1F.to_pil_image(x),
            }
    }
    return mapping[source_metadata["data_representation"]][target_metadata["data_representation"]](src_img)


def get_test_images(source_metadata, target_metadata_same_data_repr_as_source=None):
    if source_metadata["data_representation"] == "numpy.ndarray":
        return get_numpy_image(source_metadata, target_metadata_same_data_repr_as_source)
    elif source_metadata["data_representation"] == "torch.tensor":
        return get_torch_image(source_metadata, target_metadata_same_data_repr_as_source)
    elif source_metadata["data_representation"] == "tf.tensor":
        return get_tensorflow_image(source_metadata, target_metadata_same_data_repr_as_source)
    elif source_metadata["data_representation"] == "PIL.Image":
        return get_pil_image(source_metadata, target_metadata_same_data_repr_as_source)
    else:
        raise ValueError(
            f"Unsupported data representation: {source_metadata['data_representation']}"
        )


def dtype_min_max(np_type):
    is_floating = np.issubdtype(np_type, np.floating)
    if is_floating:
        return np.finfo(np_type).min, np.finfo(np_type).max
    return np.iinfo(np_type).min, np.iinfo(np_type).max


def image_data_convert_with_scaled(source_np_type, target_np_type, img):
    s_min, s_max = dtype_min_max(source_np_type)
    t_min, t_max = dtype_min_max(target_np_type)

    source_range = s_max - s_min
    target_range = t_max - t_min
    adjusted_img = img - s_min
    scaled_img = (adjusted_img / source_range) * target_range + t_min
    return scaled_img.astype(target_np_type)


def get_numpy_image(source_metadata, target_metadata=None):
    def is_invalid_numpy_metadata(metadata):
        return metadata["color_channel"] == "rgba" or metadata["color_channel"] == "graya" or metadata[
            "device"] == "gpu"

    if is_invalid_numpy_metadata(source_metadata) or (
            target_metadata is not None and is_invalid_numpy_metadata(target_metadata)):
        raise ValueError(f"Unsupported metadata for numpy.ndarray: {source_metadata} or {target_metadata}")
    r, g, b = get_r_g_b()
    img = np.stack([r, g, b], axis=0)  # [3, H, W] uint8 rgb channel first

    def convert_numpy_uint8_to_dtype(img, img_dtype, dtype):
        if dtype == "uint8":
            img = ski.util.img_as_ubyte(img)
        elif dtype == "uint16":
            img = ski.util.img_as_uint(img)
        elif dtype == "uint32":
            img = image_data_convert_with_scaled(img.dtype, np.uint32, img)
        elif dtype == "int8":
            img = image_data_convert_with_scaled(img.dtype, np.int8, img)
        elif dtype == "int16":
            img = ski.util.img_as_int(img)
        elif dtype == "int32":
            img = image_data_convert_with_scaled(img.dtype, np.int32, img)
        elif dtype == "float32(0to1)":
            if img_dtype == "float32(-1to1)":
                img = img * 0.5 + 0.5
            elif img_dtype == "float64(0to1)" or img_dtype == "double(0to1)":
                img = img.astype(np.float32)
            else:
                # from the unsigned integer type
                img = ski.util.img_as_float32(img)
        elif dtype == "float32(-1to1)":
            # from the signed integer type
            if img.dtype.kind == 'u' or img_dtype == "float32(0to1)":
                img = ski.util.img_as_float32(img)
                img = img * 2 - 1
            elif img_dtype == "float64(-1to1)" or img_dtype == "double(-1to1)":  # from the double type
                img = img.astype(np.float32)
            else:
                img = ski.util.img_as_float32(img)
        elif dtype == "float64(0to1)":
            if img_dtype == "float64(-1to1)":
                img = img * 0.5 + 0.5
            elif img_dtype == "float32(0to1)" or img_dtype == "double(0to1)":
                img = img.astype(np.float64)
            else:
                # from the unsigned integer type
                img = ski.util.img_as_float64(img)
        elif dtype == "float64(-1to1)":
            # from the signed integer type
            if img.dtype.kind == 'u' or img_dtype == "float64(0to1)":
                img = ski.util.img_as_float64(img)
                img = img * 2 - 1
            elif img_dtype == "float32(-1to1)" or img_dtype == "double(-1to1)":
                img = img.astype(np.float64)
            else:
                img = ski.util.img_as_float64(img)
        elif dtype == "double(0to1)":
            if img_dtype == "double(-1to1)":
                img = img * 0.5 + 0.5
            elif img_dtype == "float32(0to1)" or img_dtype == "float64(0to1)":
                img = img.astype(np.float64)
            else:
                # from the unsigned integer type
                img = ski.util.img_as_float64(img)
        elif dtype == "double(-1to1)":
            # from the signed integer type
            if img.dtype.kind == 'u' or img_dtype == "float64(0to1)":
                img = ski.util.img_as_float64(img)
                img = img * 2 - 1
            elif img_dtype == "float32(-1to1)" or img_dtype == "float64(-1to1)":
                img = img.astype(np.float64)
            else:
                img = ski.util.img_as_float64(img)
        return img

    def color_to_grayscale(color_img_channle_first, color_channel):
        img = color_img_channle_first.copy()
        type_in = img.dtype
        if color_channel == 'rgb':
            img = 0.299 * img[0] + 0.587 * img[1] + 0.114 * img[2]
        elif color_channel == 'bgr':
            img = 0.299 * img[2] + 0.587 * img[1] + 0.114 * img[0]
        else:
            raise ValueError(f"Unsupported color channel: {color_channel}")
        img = np.expand_dims(img, axis=0)  # [1, H, W]
        return img.astype(type_in)

    def grayscale_to_rgb_or_bgr(img):
        img = np.repeat(img, repeats=3, axis=0)
        return img

    source_img = convert_numpy_uint8_to_dtype(img, 'uint8', source_metadata["image_data_type"])
    if source_metadata["color_channel"] == "gray":
        source_img = color_to_grayscale(source_img, 'rgb')  # [1, H, W]
    elif source_metadata["color_channel"] == "bgr":
        source_img = source_img[::-1, ...]

    target_img = None
    if target_metadata is not None:
        if source_metadata["color_channel"] != "gray" and target_metadata["color_channel"] == "gray":
            if source_metadata['color_channel'] == 'bgr':
                target_img = color_to_grayscale(source_img, 'bgr')   # [1, H, W]
            else:
                target_img = color_to_grayscale(source_img, 'rgb')   # [1, H, W]
        elif source_metadata["color_channel"] == "gray" and target_metadata["color_channel"] != "gray":
            target_img = grayscale_to_rgb_or_bgr(source_img)
        elif source_metadata["color_channel"] == "rgb" and target_metadata["color_channel"] == "bgr":
            target_img = source_img[::-1, ...]
        elif source_metadata["color_channel"] == "bgr" and target_metadata["color_channel"] == "rgb":
            target_img = source_img[::-1, ...]
        else:
            target_img = source_img

        if target_metadata['image_data_type'] != source_metadata['image_data_type']:
            target_img = convert_numpy_uint8_to_dtype(target_img, source_metadata["image_data_type"], target_metadata["image_data_type"])

    def convert_other_attributes(img, metadata):
        if metadata is None:
            return None
        # img [3, H, W] or [1, H, W]
        if metadata["color_channel"] == "gray" and metadata["channel_order"] == "none":
            img = np.squeeze(img, axis=0)  # [H, W]
        elif metadata["channel_order"] == "channel last":
            img = np.transpose(img, (1, 2, 0))  # [H, W, 3] or [H, W, 1]
        if metadata["minibatch_input"]:
            img = img[np.newaxis, ...]

        return img

    return convert_other_attributes(source_img, source_metadata), convert_other_attributes(target_img, target_metadata)


def get_torch_image(source_metadata, target_metadata=None):
    r, g, b = get_r_g_b()
    source_img = torch.stack([torch.from_numpy(r), torch.from_numpy(g), torch.from_numpy(b)], dim=0)  # [3, H, W] uint8
    source_img = torch_to_dtype(source_img, source_metadata)
    if source_metadata["color_channel"] == "gray":
        source_img = V1F.rgb_to_grayscale(source_img)  # [1, H, W]

    target_img = None
    if target_metadata is not None:
        if source_metadata["color_channel"] != "gray" and target_metadata["color_channel"] == "gray":
            target_img = V1F.rgb_to_grayscale(source_img)  # [1, H, W]
        elif source_metadata["color_channel"] == "gray" and target_metadata["color_channel"] != "gray":
            target_img = source_img.repeat(3, 1, 1)  # [3, H, W]
        else:
            target_img = source_img
        if target_metadata['image_data_type'] != source_metadata['image_data_type']:
            target_img = torch_to_dtype(target_img, target_metadata)

    def convert_other_attributes(img, metadata):
        if metadata is None:
            return None
        # img [3, H, W] or [1, H, W]
        if metadata["color_channel"] == "gray":
            if metadata["channel_order"] == "channel last":
                img = img.permute(1, 2, 0)  # [H, W, 1]
            elif metadata["channel_order"] == "none":
                img = img.squeeze(0)  # [H, W]
        elif metadata["color_channel"] == "rgb" and metadata["channel_order"] == "channel last":
            img = img.permute(1, 2, 0)  # [H, W, 3]

        if metadata["minibatch_input"]:
            img = img.unsqueeze(0)
        if metadata["device"] == "gpu":
            img = img.cuda()
        return img

    return convert_other_attributes(source_img, source_metadata), convert_other_attributes(target_img, target_metadata)


def torch_to_dtype(source_img, metadata):
    # Slightly different from V1F.to_dtype and this is more common conversion code between uint8 and float32
    if source_img.dtype == torch.uint8 and metadata["image_data_type"] == "float32(0to1)":
        return (source_img / 255.0).to(torch.float32)
    elif source_img.dtype == torch.float32 and metadata["image_data_type"] == "uint8":
        return (source_img * 255).to(torch.uint8)
    else:
        dtype_mapping = {
            "uint8": torch.uint8,
            "int8": torch.int8,
            "int16": torch.int16,
            "int32": torch.int32,
            "int64": torch.int64,
            "float32(0to1)": torch.float32,
            "float64(0to1)": torch.double,
            "double(0to1)": torch.double,
        }
        return V2F.to_dtype(source_img, dtype_mapping[metadata["image_data_type"]], scale=True)


def get_tensorflow_image(source_metadata, target_metadata=None):
    r, g, b = get_r_g_b()
    source_img = tf.stack([tf.convert_to_tensor(r / 255.0, dtype=tf.float32),
                           tf.convert_to_tensor(g / 255.0, dtype=tf.float32),
                           tf.convert_to_tensor(b / 255.0, dtype=tf.float32), ],
                          axis=-1)  # [H, W, 3] float32 rgb channel last

    dtype_mapping = {
        "uint8": tf.uint8,
        "uint16": tf.uint16,
        "uint32": tf.uint32,
        "uint64": tf.uint64,
        "int8": tf.int8,
        "int16": tf.int16,
        "int32": tf.int32,
        "int64": tf.int64,
        "float16(0to1)": tf.float16,
        "float32(0to1)": tf.float32,
        "float64(0to1)": tf.float64,
        "double(0to1)": tf.float64,
    }

    source_img = tf.image.convert_image_dtype(source_img, dtype=dtype_mapping[source_metadata["image_data_type"]])
    if source_metadata["color_channel"] == "gray":
        source_img = tf.image.rgb_to_grayscale(source_img)  # [H, W, 1]

    target_img = None
    if target_metadata is not None:
        if source_metadata["color_channel"] != "gray" and target_metadata["color_channel"] == "gray":
            # if target_metadata['image_data_type'] != 'uint8':
            target_img = tf.image.rgb_to_grayscale(source_img)  # [H, W, 1]

        elif source_metadata["color_channel"] == "gray" and target_metadata["color_channel"] != "gray":
            target_img = tf.image.grayscale_to_rgb(source_img)
        else:
            target_img = source_img
        if target_metadata['image_data_type'] != source_metadata['image_data_type']:
            target_img = tf.image.convert_image_dtype(target_img,
                                                      dtype=dtype_mapping[target_metadata["image_data_type"]])

    def convert_other_attributes(img, metadata):
        if metadata is None:
            return None
        # img [H, W, 3] or [H, W, 1]
        if metadata["color_channel"] == "gray" and metadata["channel_order"] == "none":
            img = tf.squeeze(img, axis=-1)  # [H, W]
        elif metadata["color_channel"] in ["rgb", "gray"] and metadata["channel_order"] == "channel first":
            img = tf.transpose(img, perm=[2, 0, 1])  # [3, H, W] or [1, H, W]

        if metadata["minibatch_input"]:
            img = tf.expand_dims(img, 0)

        if metadata['device'] == 'gpu':
            with tf.device('/GPU:0'):
                img = tf.identity(img)
        return img

    return convert_other_attributes(source_img, source_metadata), convert_other_attributes(target_img, target_metadata)


def get_pil_image(source_metadata, target_metadata=None):
    def is_invalid_pil_metadata(metadata):
        return metadata["minibatch_input"] or metadata["image_data_type"] != 'uint8' or metadata["device"] == 'gpu' or \
            metadata["channel_order"] == 'channel first'

    if is_invalid_pil_metadata(source_metadata) or (
            target_metadata is not None and is_invalid_pil_metadata(target_metadata)):
        raise ValueError(
            f"Unsupported metadata for PIL.Image: {source_metadata} or {target_metadata}"
        )
    r, g, b = get_r_g_b()
    img_array = np.stack([r, g, b], axis=-1)
    base_img = Image.fromarray(img_array, mode='RGB')  # [H, W, 3] uint8 rgb channel last

    def convert_color_channel_channel_order(img, metadata):
        if metadata is None:
            return None
        if metadata["color_channel"] == "gray" and metadata['channel_order'] == 'none':
            img = img.convert('L')  # [H, W]
        if metadata["color_channel"] == "rgb" and metadata['channel_order'] == 'channel last':
            img = img.convert('RGB')  # [H, W, 3]
        elif metadata["color_channel"] == "rgba":
            img = img.convert('RGBA')
        elif metadata["color_channel"] == "graya":
            img = img.convert('LA')  # [H, W, 2]
        return img

    source_img = convert_color_channel_channel_order(base_img, source_metadata)
    return source_img, convert_color_channel_channel_order(source_img, target_metadata)


def is_tensorflow_image_equal(image1, image2, tolerance=1e-5):
    equality = tf.math.equal(image1, image2)
    if image1.dtype.is_floating:
        close_enough = tf.less_equal(tf.abs(image1 - image2), tolerance)
        combined_check = tf.logical_or(equality, close_enough)
    else:
        combined_check = equality
    return tf.reduce_all(combined_check)


def is_image_equal(image1, image2, tolerance=1):
    try:
        if type(image1) != type(image2):
            return False
        if isinstance(image1, np.ndarray):
            return np.allclose(image1, image2, tolerance)
        elif isinstance(image1, torch.Tensor):
            return torch.allclose(image1, image2, rtol=tolerance)
        elif isinstance(image1, tf.Tensor):
            return is_tensorflow_image_equal(image1, image2, tolerance)
        elif isinstance(image1, Image.Image):
            return np.allclose(np.array(image1), np.array(image2), tolerance)
    except Exception:
        pass
    return False
