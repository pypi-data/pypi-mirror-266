from .edge_factories import (Conversion, EdgeFactory, FactoriesCluster, ConversionForMetadataPair,
                             factories_clusters, list_of_conversion_for_metadata_pair)
from .knowledge_graph import KnowledgeGraph
from .constructor import KnowledgeGraphConstructor
from .metedata import *


constructor = KnowledgeGraphConstructor(metadata_values, factories_clusters, list_of_conversion_for_metadata_pair)
constructor.build()


def get_knowledge_graph_constructor():
    return constructor
