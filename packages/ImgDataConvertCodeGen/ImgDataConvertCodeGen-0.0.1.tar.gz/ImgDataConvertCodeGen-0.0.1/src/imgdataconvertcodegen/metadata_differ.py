def are_both_same_data_repr(metadata_a, metadata_b, data_repr):
    return metadata_a.get('data_representation') == data_repr and metadata_b.get('data_representation') == data_repr


def is_differ_value_for_key(metadata_a, metadata_b, key):
    return metadata_a[key] != metadata_b[key]
