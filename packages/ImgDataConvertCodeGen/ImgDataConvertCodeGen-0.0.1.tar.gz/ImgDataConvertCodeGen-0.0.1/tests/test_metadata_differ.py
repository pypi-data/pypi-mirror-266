from src.imgdataconvertcodegen import are_both_same_data_repr, is_differ_value_for_key


def test_both_metadata_match_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {'data_representation': 'torch.tensor'}
    data_repr = 'torch.tensor'
    assert are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return True when both metadata have the same data_representation matching data_repr"


def test_one_metadata_missing_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {}
    data_repr = 'torch.tensor'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when one metadata is missing the data_representation key"


def test_one_metadata_different_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {'data_representation': 'numpy.ndarray'}
    data_repr = 'torch.tensor'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when one metadata has a different data_representation value"


def test_both_metadata_missing_data_repr():
    metadata_a = {}
    metadata_b = {}
    data_repr = 'torch.tensor'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when both metadata are missing the data_representation key"


def test_both_metadata_different_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {'data_representation': 'numpy.ndarray'}
    data_repr = 'PIL'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when both metadata have different data_representation values not matching data_repr"


def test_is_differ_value_for_key_true():
    metadata_a = {'key1': 'value1', 'key2': 'value2'}
    metadata_b = {'key1': 'diff_value1', 'key2': 'value2'}
    assert is_differ_value_for_key(metadata_a, metadata_b, 'key1'), \
        "Should return True when only the specified key differs"


def test_is_differ_value_for_key_false():
    metadata_a = {'key1': 'value1', 'key2': 'value2'}
    metadata_b = {'key1': 'value1', 'key2': 'value2'}
    assert not is_differ_value_for_key(metadata_a, metadata_b, 'key1'), \
        "Should return False when there are no differences, even for the specified key"
