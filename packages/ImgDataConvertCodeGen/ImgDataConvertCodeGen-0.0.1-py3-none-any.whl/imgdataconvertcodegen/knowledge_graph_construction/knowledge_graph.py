import math
from typing import Union, List

import networkx as nx

from .io import save_graph, load_graph
from .metedata import Metadata, encode_metadata, decode_metadata, decode_separator


class KnowledgeGraph:
    _graph = None

    def __init__(self):
        self._graph = nx.DiGraph()

    def clear(self):
        self._graph.clear()

    @property
    def nodes(self):
        encoded_nodes = self._graph.nodes
        return [decode_metadata(node) for node in encoded_nodes]

    @property
    def edges(self):
        encoded_edges = self._graph.edges
        return [
            (decode_metadata(edge[0]), decode_metadata(edge[1]))
            for edge in encoded_edges
        ]

    def add_node(self, node):
        self._graph.add_node(encode_metadata(node))

    def add_edge(
        self,
        source: Metadata,
        target: Metadata,
        conversion,
        time_cost=math.inf,
        factory=None,
    ):
        self._graph.add_edge(
            encode_metadata(source),
            encode_metadata(target),
            conversion=conversion,
            time_cost=time_cost,
            factory=factory,
        )

    def get_edge_data(self, source: Metadata, target: Metadata):
        return self._graph.get_edge_data(
            encode_metadata(source), encode_metadata(target)
        )

    def set_edge_attribute(self, source: Metadata, target: Metadata, attribute, value):
        self._graph[encode_metadata(source)][encode_metadata(target)][attribute] = value

    def save_to_file(self, path):
        save_graph(self._graph, path)

    def load_from_file(self, path):
        self._graph = load_graph(path)

    def cost_function_in_AStar(self, u, v, edge_attributes):
        if "normalized_time_cost" not in edge_attributes:
            return 1
        time_cost = edge_attributes["normalized_time_cost"]
        step_cost = 1

        v_metadata = decode_metadata(v)
        gpu_penalty = 0.2 if v_metadata["device"] == "gpu" else 0

        total_cost = time_cost + step_cost + gpu_penalty
        return total_cost

    def heuristic_in_AStar(self, u, v):
        u_metadata = u.split(decode_separator())
        v_metadata = v.split(decode_separator())
        L1_loss = sum(
            [1 for i in range(len(u_metadata)) if u_metadata[i] != v_metadata[i]]
        )
        return L1_loss

    def get_shortest_path(
        self, source_metadata, target_metadata
    ) -> Union[List[str], None]:
        try:
            path = nx.astar_path(
                self._graph,
                encode_metadata(source_metadata),
                encode_metadata(target_metadata),
                heuristic=self.heuristic_in_AStar,
                weight=self.cost_function_in_AStar,
            )
            return [decode_metadata(node) for node in path]
        except nx.NetworkXNoPath:
            return None

    def __str__(self):
        return f"Knowledge Graph with {len(self._graph)} nodes and {len(self._graph.edges)} edges."
