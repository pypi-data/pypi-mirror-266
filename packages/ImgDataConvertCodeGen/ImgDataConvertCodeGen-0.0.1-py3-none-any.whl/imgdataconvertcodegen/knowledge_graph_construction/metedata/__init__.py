from .type import MetadataValues, Metadata
from .util import *

metadata_values: MetadataValues = {
    "data_representation": ["torch.tensor", "numpy.ndarray", "PIL.Image", "tf.tensor"],
    "color_channel": ['rgb', 'bgr', 'gray', 'rgba', 'graya'],
    "channel_order": ['channel last', 'channel first', 'none'],
    "minibatch_input": [True, False],
    # image dtype conversion involves type convert and intensity range rescale
    # intensity range for floating point can be -1 to 1 or 0 to 1 from
    # https://scikit-image.org/docs/stable/user_guide/data_types.html
    "image_data_type": ['uint8', 'uint16', 'uint32', 'uint64',
                        'int8', 'int16', 'int32', 'int64',
                        'float32(0to1)', 'float32(-1to1)',
                        'float64(0to1)', 'float64(-1to1)',
                        'double(0to1)', 'double(-1to1)',
                        ],
    "device": ['cpu', 'gpu']
}
