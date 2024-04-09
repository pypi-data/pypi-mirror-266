import pytest

from src.imgdataconvertcodegen.knowledge_graph_construction.metedata.util import find_closest_metadata, encode_metadata, \
    decode_metadata


def test_encode_to_string():
    metadata = {
        "data_representation": "torch.tensor",
        "color_channel": 'rgb',
        "channel_order": 'channel first',
        "minibatch_input": True,
        "image_data_type": 'uint8',
        "device": 'gpu'
    }
    encoded = encode_metadata(metadata)
    assert encoded == 'torch.tensor_rgb_channel first_True_uint8_gpu'


def test_decode_to_dict():
    metadata_str = 'torch.tensor_rgb_channel first_True_float64(-1to1)_gpu'
    decoded = decode_metadata(metadata_str)
    assert decoded == {
        "data_representation": "torch.tensor",
        "color_channel": 'rgb',
        "channel_order": 'channel first',
        "minibatch_input": True,
        "image_data_type": 'float64(-1to1)',
        "device": 'gpu'
    }


source_metadata = {
    "data_representation": "torch.tensor",
    "color_channel": "rgb",
    # Other metadata values...
}


@pytest.fixture
def candidate_metadatas():
    return [
        {"data_representation": "torch.tensor", "color_channel": "rgb"},
        {"data_representation": "numpy.ndarray", "color_channel": "rgb"},
        {"data_representation": "torch.tensor", "color_channel": "bgr"},
        {"data_representation": "tf.tensor", "color_channel": "rgba"},
    ]


def test_exact_match(candidate_metadatas):
    closest_targets = find_closest_metadata(source_metadata, candidate_metadatas)
    assert closest_targets == candidate_metadatas[0]


def test_representation_match_no_channel_match(candidate_metadatas):
    modified_source = source_metadata.copy()
    modified_source["color_channel"] = "rgba"
    closest_targets = find_closest_metadata(modified_source, candidate_metadatas)
    assert closest_targets == candidate_metadatas[0]


def test_no_representation_match(candidate_metadatas):
    modified_source = source_metadata.copy()
    modified_source["data_representation"] = "unknown"
    closest_targets = find_closest_metadata(modified_source, candidate_metadatas)
    assert closest_targets == candidate_metadatas[0]


def test_rgb_bgr_match(candidate_metadatas):
    modified_source = source_metadata.copy()
    modified_source["color_channel"] = "bgr"
    modified_source["data_representation"] = "numpy.ndarray"
    closest_targets = find_closest_metadata(modified_source, candidate_metadatas)
    assert closest_targets == candidate_metadatas[1]


def test_empty_candidate_list():
    closest_targets = find_closest_metadata(source_metadata, [])
    assert closest_targets is None


def test_one_candidata():
    closest_targets = find_closest_metadata(source_metadata, [source_metadata])
    assert closest_targets == source_metadata
