import os

import numpy as np
import pytest
import torch

from src.imgdataconvertcodegen.code_generator import ConvertCodeGenerator
from src.imgdataconvertcodegen.knowledge_graph_construction import KnowledgeGraph
from .data_for_tests.nodes_edges import new_node, test_nodes


@pytest.fixture
def code_generator():
    kg = KnowledgeGraph()
    kg.load_from_file(os.path.join(os.path.dirname(__file__), 'data_for_tests/kg_5nodes_4edges.json'))
    return ConvertCodeGenerator(kg)


def test_code_generation_using_metadata(code_generator):
    kg = code_generator.knowledge_graph
    source_image = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
    expected_image = torch.from_numpy(source_image).permute(2, 0, 1).unsqueeze(0)

    # Prepare a custom scope that includes both global and local variables to ensure that the dynamically executed code
    # has access to necessary pre-defined variables and can also store new variables such as 'target_result'.
    # This is crucial in the pytest environment where test function scopes are isolated, and dynamically defined
    # variables might not be directly accessible due to Python's scoping rules.
    scope = globals().copy()
    scope.update(locals())

    convert_code = code_generator.get_conversion('source_image', test_nodes[0],
                                                 'target_image', new_node)
    exec(convert_code, scope)

    # Retrieve 'target_image' from the custom scope, ensuring accessibility despite the isolated test function scope
    actual_image = scope.get('target_image')

    assert torch.equal(expected_image, actual_image), 'expected and actual images are not equal'
