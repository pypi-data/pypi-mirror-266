import os
from unittest.mock import patch, mock_open

import networkx as nx
import pytest

from src.imgdataconvertcodegen.knowledge_graph_construction.io import save_graph, load_graph


def test_load_graph_from_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'data_for_tests', 'kg_5nodes_4edges.json')

    graph = load_graph(json_file_path)

    assert isinstance(graph, nx.DiGraph)
    assert len(graph.nodes) == 5, "Graph should have 5 nodes, but it has " + str(len(graph.nodes))
    assert len(graph.edges) == 4, "Graph should have 4 edges, but it has " + str(len(graph.edges))


def test_load_graph_with_invalid_path():
    with pytest.raises(FileNotFoundError):
        load_graph("path/to/nonexistent_file.json")


def test_save_graph_to_file():
    mock_graph = nx.DiGraph()
    mock_graph.add_edge('node1', 'node2')

    with patch("builtins.open", mock_open()) as mocked_file, \
            patch("json.dumps", return_value='mock_json_data') as mock_json_dumps:
        save_graph(mock_graph, "mock_save_path.json")
        mock_json_dumps.assert_called_once_with(mock_graph, default=nx.node_link_data)
        mocked_file.assert_called_once_with("mock_save_path.json", "w")
        mocked_file().write.assert_called_once_with('mock_json_data')


def test_save_graph_with_invalid_path():
    mock_graph = nx.DiGraph()
    mock_graph.add_edge('node1', 'node2')

    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            save_graph(mock_graph, "invalid/path/mock_save_path.json")
