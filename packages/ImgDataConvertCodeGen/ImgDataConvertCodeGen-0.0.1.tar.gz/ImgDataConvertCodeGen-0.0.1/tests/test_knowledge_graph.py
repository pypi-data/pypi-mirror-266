import os
from unittest.mock import patch

import networkx as nx
import pytest

from src.imgdataconvertcodegen.knowledge_graph_construction import KnowledgeGraph, encode_metadata
from .data_for_tests.nodes_edges import test_nodes, test_edges, new_node, new_edge


@pytest.fixture
def kg():
    kg = KnowledgeGraph()
    for edge in test_edges:
        kg.add_edge(edge[0], edge[1], edge[2])
    return kg


def test_knowledge_graph_init(kg):
    assert isinstance(kg._graph, nx.DiGraph), "The graph object is not an instance of nx.DiGraph"


def test_add_new_node(kg):
    kg.add_node(new_node)
    assert new_node in kg.nodes, f"New node was not added to the graph"


def test_add_edge(kg):
    kg.add_node(new_node)
    kg.add_edge(new_edge[0], new_edge[1], new_edge[2])
    assert kg.get_edge_data(new_edge[0], new_edge[1])['conversion'] == new_edge[2], \
        f"Expected {new_edge[2]}, got {kg.get_edge_data(new_edge[0], new_edge[1])['conversion']}"


def test_get_edge(kg):
    expected_edge = test_edges[0]
    assert kg.get_edge_data(expected_edge[0], expected_edge[1])['conversion'] == expected_edge[2], \
        f"Expected {expected_edge[2]}, got {kg.get_edge_data(1, 2)}"


def test_edge_failure(kg):
    assert kg.get_edge_data(test_nodes[3], test_nodes[3]) is None, f"Expected None"


def test_save_to_file(kg):
    with patch('src.imgdataconvertcodegen.knowledge_graph_construction.knowledge_graph.save_graph') as mock_save_graph:
        expected_file_path = os.path.join('data_for_tests', 'kg_5nodes_4edges.json')
        kg.save_to_file(expected_file_path)
        mock_save_graph.assert_called_once_with(kg._graph, expected_file_path)


def test_get_shortest_path(kg):
    kg.add_node(new_node)
    kg.add_edge(new_edge[0], new_edge[1], new_edge[2])

    path = kg.get_shortest_path(test_nodes[0], new_node)
    expected_path = [test_nodes[0], test_nodes[2], test_nodes[3], new_node]
    assert path == expected_path, f"Expected {expected_path}, got {path}"


def test_get_shortest_path_no_path(kg):
    path = kg.get_shortest_path(test_nodes[2], test_nodes[0])
    assert path is None, f"Expected None, got {path}"


def test_get_shortest_path_same_node(kg):
    path = kg.get_shortest_path(test_nodes[0], test_nodes[0])
    assert path == [test_nodes[0]], f"Expected {test_nodes[0]}, got {path}"


def test_knowledge_graph_str(kg):
    expected_str = "Knowledge Graph with 4 nodes and 3 edges."
    assert str(kg) == expected_str, f"Expected {expected_str}, got {str(kg)}"


def test_heuristic_function(kg):
    u = encode_metadata(test_nodes[0])
    v = encode_metadata(test_nodes[0])
    assert kg.heuristic_in_AStar(u, v) == 0, f"Expected 0, got {kg.heuristic_in_AStar(u, v)}"

    u = encode_metadata(test_nodes[0])
    v = encode_metadata(test_nodes[1])
    assert kg.heuristic_in_AStar(u, v) == 1, f"Expected 1, got {kg.heuristic_in_AStar(u, v)}"

    u = encode_metadata(test_nodes[0])
    v = encode_metadata(test_nodes[3])
    assert kg.heuristic_in_AStar(u, v) == 2, f"Expected 2, got {kg.heuristic_in_AStar(u, v)}"

    u = encode_metadata(test_nodes[0])
    v = encode_metadata(new_node)
    assert kg.heuristic_in_AStar(u, v) == 3, f"Expected 3, got {kg.heuristic_in_AStar(u, v)}"
