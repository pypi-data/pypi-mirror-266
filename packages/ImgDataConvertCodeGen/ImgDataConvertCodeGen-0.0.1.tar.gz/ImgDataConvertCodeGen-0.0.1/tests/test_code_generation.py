import os.path
from unittest.mock import MagicMock

import pytest

from src.imgdataconvertcodegen.code_generator import ConvertCodeGenerator
from src.imgdataconvertcodegen.knowledge_graph_construction import KnowledgeGraph
from .data_for_tests.nodes_edges import new_node, test_nodes, all_nodes


@pytest.fixture
def code_generator():
    kg = KnowledgeGraph()
    kg.load_from_file(os.path.join(os.path.dirname(__file__), 'data_for_tests/kg_5nodes_4edges.json'))
    return ConvertCodeGenerator(kg)


def test_convert_code_generator_init(code_generator):
    assert len(code_generator.knowledge_graph.nodes) == 5, \
        "Expected 5, but got " + str(code_generator.knowledge_graph.nodes)


def test_knowledge_graph_property(code_generator):
    new_kg = KnowledgeGraph()
    code_generator.knowledge_graph = new_kg
    assert code_generator.knowledge_graph == new_kg, (
            "Expected " + str(new_kg) + ", but got " + str(code_generator.knowledge_graph))


def test_conversion_path(code_generator):
    expected_path = ['node1', 'node2']
    code_generator.knowledge_graph.get_shortest_path = MagicMock()
    code_generator.knowledge_graph.get_shortest_path.return_value = expected_path
    actual = code_generator.get_convert_path({"source": "source_metadata"}, {"target": "target_metadata"})

    code_generator.knowledge_graph.get_shortest_path.assert_called_once_with({"source": "source_metadata"},
                                                                             {"target": "target_metadata"})
    assert actual == expected_path, "The returned path does not match the expected path."


def test_generate_conversion_no_path(code_generator):
    source_var = 'source_var'
    target_var = 'result'
    generated_code = code_generator.get_conversion(source_var, new_node, target_var, test_nodes[0])
    assert generated_code is None, "Expected None, but got " + str(generated_code)
    assert list(code_generator._cache.values()) == [None]


def test_generate_conversion_same_type(code_generator):
    source_var = 'source_var'
    target_var = 'result'
    generated_code = code_generator.get_conversion(source_var, test_nodes[0], target_var, test_nodes[0])
    expected_code = f'{target_var} = {source_var}'

    assert generated_code == expected_code, "Expected " + expected_code + ", but got " + str(generated_code)
    assert list(code_generator._cache.values()) == [[test_nodes[0]]]


def test_generate_conversion_multiple_steps(code_generator):
    source_var = 'source_var'
    target_var = 'result'
    generated_code = code_generator.get_conversion(source_var, test_nodes[0], target_var, new_node)

    expected_code = ('import torch\n'
                     'image = torch.from_numpy(source_var)\n'
                     'image = image.permute(2, 0, 1)\n'
                     'result = torch.unsqueeze(image, 0)')

    assert generated_code == expected_code, f'Expected {expected_code}, but got {str(generated_code)}'


def test_generate_conversion_using_cache(code_generator):
    source_var = 'source_var'
    target_var = 'result'

    code_generator.get_conversion(source_var, test_nodes[0], target_var, new_node)
    assert list(code_generator._cache.values()) == [
        [all_nodes[0], all_nodes[2], all_nodes[3], all_nodes[4]]], "Code not cached"

    code_from_cache = code_generator.get_conversion(source_var, test_nodes[0], target_var, new_node)
    expected_code = ('import torch\n'
                     'image = torch.from_numpy(source_var)\n'
                     'image = image.permute(2, 0, 1)\n'
                     'result = torch.unsqueeze(image, 0)')

    assert code_from_cache == expected_code, f'Expected {expected_code}, but got {str(code_from_cache)}'
