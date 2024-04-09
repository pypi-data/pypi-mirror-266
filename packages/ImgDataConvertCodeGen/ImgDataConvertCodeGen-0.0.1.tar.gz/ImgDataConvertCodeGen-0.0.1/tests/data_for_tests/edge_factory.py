from src.imgdataconvertcodegen import are_both_same_data_repr


def numpy_rgb_to_bgr(source_metadata, target_metadata):
    if not are_both_same_data_repr(source_metadata, target_metadata, 'numpy.ndarray'):
        return None
    if source_metadata.get('color_channel') == 'rgb' and target_metadata.get('color_channel') == 'bgr':
        return "", "def convert(var):\n  return var[:, :, ::-1]"
    return None


def numpy_to_torch(source_metadata, target_metadata):
    if (source_metadata.get('data_representation') == 'numpy.ndarray' and
            target_metadata.get('data_representation') == 'torch.tensor'):
        return "import torch", "def convert(var):\n  return torch.from_numpy(var)"
    return None


def torch_channel_order_last_to_first(source_metadata, target_metadata):
    if not are_both_same_data_repr(source_metadata, target_metadata, 'torch.tensor'):
        return None
    if (source_metadata.get('channel_order') == 'channel last' and
            target_metadata.get('channel_order') == 'channel first'):
        if source_metadata.get('minibatch_input'):
            return "", "def convert(var):\n  return var.permute(0, 3, 1, 2)"
        return "", "def convert(var):\n  return var.permute(2, 0, 1)"
    return None


def torch_minibatch_input_false_to_true(source_metadata, target_metadata):
    if not are_both_same_data_repr(source_metadata, target_metadata, 'torch.tensor'):
        return None
    if (not source_metadata.get('minibatch_input')) and target_metadata.get('minibatch_input'):
        return "import torch", "def convert(var):\n  return torch.unsqueeze(var, 0)"

    return None


edge_factory_examples = [
    numpy_rgb_to_bgr,
    numpy_to_torch,
    torch_channel_order_last_to_first,
    torch_minibatch_input_false_to_true]


def numpy_bgr_to_rgb(source_metadata, target_metadata):
    if not are_both_same_data_repr(source_metadata, target_metadata, 'numpy.ndarray'):
        return None
    if target_metadata.get('color_channel') == 'rgb' and source_metadata.get('color_channel') == 'bgr':
        return "", "def convert(var):\n  return var[:, :, ::-1]"
    return None


new_edge_factory = numpy_bgr_to_rgb
