from .type import Conversion, FactoriesCluster, ConversionForMetadataPair
from ...metadata_differ import are_both_same_data_repr


def is_attribute_value_valid_for_pil(metadata):
    # https://pillow.readthedocs.io/en/stable/handbook/concepts.html
    allowed_values = {
        "color_channel": ['rgb', 'gray', 'rgba', 'graya'],
        "channel_order": ['channel last', 'none'],
        "minibatch_input": [False],
        # Pillow doesn’t yet support multichannel images with a depth of more than 8 bits per channel.
        "image_data_type": ['uint8'],
        "device": ['cpu'],
    }
    for key, allowed_values in allowed_values.items():
        if key in metadata and metadata[key] not in allowed_values:
            return False
    return True


def is_metadata_valid_for_pil(metadata):
    if metadata['color_channel'] == 'gray' and metadata['channel_order'] != 'none':
        return False
    if metadata['color_channel'] != 'gray' and metadata['channel_order'] == 'none':
        return False
    return True


def can_use_factories_in_cluster(source_metadata, target_metadata):
    return (
            are_both_same_data_repr(source_metadata, target_metadata, "PIL.Image")
            and is_attribute_value_valid_for_pil(source_metadata)
            and is_attribute_value_valid_for_pil(target_metadata)
            and is_metadata_valid_for_pil(source_metadata)
            and is_metadata_valid_for_pil(target_metadata)
    )


def rgba_to_rgb(source_metadata, target_metadata) -> Conversion:
    if source_metadata.get("color_channel") == "rgba" and target_metadata.get("color_channel") == "rgb":
        return "", 'def convert(var):\n  return var.convert("RGB")'


def rgba_to_graya(source_metadata, target_metadata) -> Conversion:
    if source_metadata.get("color_channel") == "rgba" and target_metadata.get("color_channel") == "graya":
        return '', 'def convert(var):\n  return var.convert("LA")'


factories_cluster_for_pil : FactoriesCluster = (
    can_use_factories_in_cluster,
    [
        rgba_to_rgb,
        rgba_to_graya,
    ],
)

pil_graya_or_rgba_rgb_to_gray: Conversion = ('', 'def convert(var):\n  return var.convert("L")')

pil_gray_to_rgb: Conversion = ('', 'def convert(var):\n  return var.convert("RGB")')

factories_for_pil_metadata_pair: list[ConversionForMetadataPair] = [
    (
        {
            "data_representation": "PIL.Image",
            "color_channel": 'rgb',
            "channel_order": 'channel last',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        },
        {
            "data_representation": "PIL.Image",
            "color_channel": 'gray',
            "channel_order": 'none',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        }, pil_graya_or_rgba_rgb_to_gray),
    (
        {
            "data_representation": "PIL.Image",
            "color_channel": 'rgba',
            "channel_order": 'channel last',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        },
        {
            "data_representation": "PIL.Image",
            "color_channel": 'gray',
            "channel_order": 'none',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        }, pil_graya_or_rgba_rgb_to_gray),
    (
        {
            "data_representation": "PIL.Image",
            "color_channel": 'graya',
            "channel_order": 'channel last',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        },
        {
            "data_representation": "PIL.Image",
            "color_channel": 'gray',
            "channel_order": 'none',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        }, pil_graya_or_rgba_rgb_to_gray),
    (
        {
            "data_representation": "PIL.Image",
            "color_channel": 'gray',
            "channel_order": 'none',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        },
        {
            "data_representation": "PIL.Image",
            "color_channel": 'rgb',
            "channel_order": 'channel last',
            "minibatch_input": False,
            "image_data_type": 'uint8',
            "device": 'cpu',
        }, pil_gray_to_rgb),
]
