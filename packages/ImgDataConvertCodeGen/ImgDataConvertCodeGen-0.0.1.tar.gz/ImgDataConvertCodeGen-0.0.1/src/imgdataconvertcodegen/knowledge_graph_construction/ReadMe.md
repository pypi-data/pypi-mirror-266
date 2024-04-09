## Conversion Knowledge Graph
### Node structure Example
```python
image_data = {
    "data_representation": "numpy.ndarray",  # Options: numpy.ndarray, PIL.Image, torch.tensor, tf.tensor
    "color_channel": "rgb",                 # Options: rgb, gbr, gray, rgba, graya
    "channel_order": "channel last",        # Options: channel last, channel first
    "minibatch_input": False,               # Values: True, False
    "data_type": "uint8",                   # Options: uint8, uint16, uint32, float, float64, int8, int16, int32
    "device": "cpu"                         # Options: cpu, gpu
}
```
More values for each key can be found in the `metadata_values.py`.

### Edge Create Factory Example

```python
from ..metadata_differ import are_both_same_data_repr

# NOTE: the source and target metadata are only different in one attribute
# When call the function from some libaries, please start from the library name, like torch.tensor
def torch_channel_order_last_to_first(source_metadata, target_metadata):
    if not are_both_same_data_repr(source_metadata, target_metadata, 'torch.tensor'):
        return None
    if (source_metadata.get('channel_order') == 'channel last' and
            target_metadata.get('channel_order') == 'channel first'):
        if source_metadata.get('minibatch_input'):
            return "def convert(var):\n  return var.permute(0, 3, 1, 2)"
        return "def convert(var):\n  return var.permute(2, 0, 1)"
    return None
```
More metadata differ functions can be found in the `metadata_differ.py`.
More examples can be found in the `knowledge_graph_construction/default_edge_factories.py`.
