from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

from .interface_py_api import _code_generator, _constructor
from .interface_py_api import (get_conversion_code, get_convert_path, add_edge_factory_cluster,
                               add_meta_values_for_image, add_conversion_for_metadata_pairs)
from .knowledge_graph_construction import find_closest_metadata
from .metadata_differ import *

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "ImgDataConvertCodeGen"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
