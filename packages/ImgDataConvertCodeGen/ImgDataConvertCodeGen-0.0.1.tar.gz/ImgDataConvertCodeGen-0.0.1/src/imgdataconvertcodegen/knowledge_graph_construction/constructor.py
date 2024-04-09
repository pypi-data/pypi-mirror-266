import math
import timeit
import re
import itertools
import os.path
from typing import List, Union

from .knowledge_graph import KnowledgeGraph
from .metedata import MetadataValues
from .edge_factories import FactoriesCluster, ConversionForMetadataPair
from ..util import exclude_key_from_list
from ..image_data import get_input_image_and_expected_output


class KnowledgeGraphConstructor:
    _max_time_cost = 0

    def __init__(
        self,
        metadata_values: MetadataValues,
        edge_factories_clusters: list[FactoriesCluster],
        list_of_conversion_for_metadata_pair: List[ConversionForMetadataPair],
    ):
        self._metadata_values = metadata_values
        self._edge_factories_clusters = edge_factories_clusters
        self._list_of_conversion_for_metadata_pair = (
            list_of_conversion_for_metadata_pair
        )
        self._know_graph_file_path = os.path.join(
            os.path.dirname(__file__), "knowledge_graph.json"
        )
        self._graph = KnowledgeGraph()

    @property
    def knowledge_graph(self):
        return self._graph

    def clear_knowledge_graph(self):
        self._graph.clear()

    def save_knowledge_graph(self):
        self.knowledge_graph.save_to_file(self._know_graph_file_path)

    def load_knowledge_graph_from(self, path):
        self.clear_knowledge_graph()
        self.knowledge_graph.load_from_file(path)

    def build(self) -> KnowledgeGraph:
        if os.path.exists(self._know_graph_file_path):
            self.load_knowledge_graph_from(self._know_graph_file_path)
        else:
            self.build_from_scratch()
        return self.knowledge_graph

    def build_from_scratch(self):
        self.clear_knowledge_graph()
        self._create_edges_using_factories_clusters(
            self._metadata_values, self._edge_factories_clusters
        )
        self._create_edges_from_manual_annotation(
            self._list_of_conversion_for_metadata_pair
        )
        self._normalize_time_costs()
        self.save_knowledge_graph()

    def _create_edges_using_factories_clusters(
        self, metadata_values, factories_clusters: list[FactoriesCluster]
    ):
        # one property change policy.
        attributes = list(metadata_values.keys())
        attributes_values_lists = list(metadata_values.values())
        for attribute_values in itertools.product(*attributes_values_lists):
            source_metadata = dict(zip(attributes, attribute_values))
            for attribute in metadata_values.keys():
                for new_attribute_v in exclude_key_from_list(
                    metadata_values[attribute], source_metadata[attribute]
                ):
                    self._create_edge(
                        source_metadata, attribute, new_attribute_v, factories_clusters
                    )

    def _create_edge(
        self,
        source,
        changed_attribute: str,
        new_attribute_value,
        factories_clusters: list[FactoriesCluster],
    ):
        target = source.copy()
        target[changed_attribute] = new_attribute_value
        for factory_cluster in factories_clusters:
            can_use_factories_in_cluster, factories = factory_cluster
            if not can_use_factories_in_cluster(source, target):
                continue
            for factory in factories:
                function = factory(source, target)
                if function is not None:
                    self._add_edge(source, target, function, factory)

    def _create_edges_from_manual_annotation(
        self, list_of_conversion_for_metadata_pair: List[ConversionForMetadataPair]
    ):
        if list_of_conversion_for_metadata_pair is None:
            return
        for source, target, conversion in list_of_conversion_for_metadata_pair:
            self._add_edge(source, target, conversion, "manual")

    def _add_edge(self, source, target, conversion, factory=None):
        execution_time = self._execute_time_cost(source, target, conversion)
        used_factory = (
            factory
            if isinstance(factory, str)
            else f"{factory.__code__.co_name} in {factory.__code__.co_filename}"
        )
        self.knowledge_graph.add_edge(
            source,
            target,
            conversion=conversion,
            time_cost=execution_time,
            factory=used_factory,
        )
        self._set_max_time_cost(execution_time)

    def _execute_time_cost(self, source, target, conversion, repeat_count=10):
        try:
            source_image, _ = get_input_image_and_expected_output(source, target)
        except Exception as e:
            # If the conversion function cannot be executed, return infinity, for example, there is no tensorflow gpu
            # support in the environment.
            return math.inf
        setup = f"{conversion[0]}\n{conversion[1]}"
        func_name = re.search(r"(?<=def )\w+", conversion[1]).group(0)
        code = f"actual_image = {func_name}(source_image)"
        execution_time = timeit.timeit(
            stmt=code, setup=setup, number=repeat_count, globals=locals()
        )
        return execution_time / repeat_count

    def _set_max_time_cost(self, execution_time):
        if execution_time == math.inf:
            return
        if execution_time > self._max_time_cost:
            self._max_time_cost = execution_time

    def _normalize_time_costs(self):
        for source, target in self.knowledge_graph.edges:
            time_cost = self.knowledge_graph.get_edge_data(source, target)["time_cost"]
            self.knowledge_graph.set_edge_attribute(
                source,
                target,
                "normalized_time_cost",
                round(time_cost / self._max_time_cost, 3),
            )

    def add_edge_factory_cluster(self, factory_cluster: FactoriesCluster):
        self._edge_factories_clusters.append(factory_cluster)
        self._create_edges_using_factories_clusters(
            self._metadata_values, [factory_cluster]
        )
        self.save_knowledge_graph()

    def add_metadata_values(self, new_metadata: MetadataValues):
        self._create_edges_using_factories_clusters(
            new_metadata, self._edge_factories_clusters
        )
        self.save_knowledge_graph()

    def add_conversion_for_metadata_pairs(
        self, pairs: Union[List[ConversionForMetadataPair], ConversionForMetadataPair]
    ):
        if pairs is None or (isinstance(pairs, list) and len(pairs) == 0):
            return
        self._create_edges_from_manual_annotation(
            pairs if isinstance(pairs, list) else [pairs]
        )
        self.save_knowledge_graph()
