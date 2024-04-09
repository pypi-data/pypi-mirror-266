from .type import Conversion, EdgeFactory, FactoriesCluster, ConversionForMetadataPair
from .PIL import factories_cluster_for_pil, factories_for_pil_metadata_pair
from .numpy import factories_cluster_for_numpy
from .Pytorch import factories_cluster_for_Pytorch
from .Tensorflow import factories_cluster_for_tensorflow
from .inter_libs import (factories_cluster_for_numpy_pil, factories_cluster_for_numpy_torch,
                         factories_cluster_for_numpy_tensorflow, factories_cluster_for_pil_tensorflow,
                         factories_for_pil_torch_metadata_pair)

factories_clusters: list[FactoriesCluster] = [
    factories_cluster_for_pil,
    factories_cluster_for_numpy,
    factories_cluster_for_Pytorch,
    factories_cluster_for_tensorflow,
    factories_cluster_for_numpy_pil,
    factories_cluster_for_numpy_torch,
    factories_cluster_for_numpy_tensorflow,
    factories_cluster_for_pil_tensorflow

]

list_of_conversion_for_metadata_pair: list[ConversionForMetadataPair] = (factories_for_pil_metadata_pair +
                                                                         factories_for_pil_torch_metadata_pair)
