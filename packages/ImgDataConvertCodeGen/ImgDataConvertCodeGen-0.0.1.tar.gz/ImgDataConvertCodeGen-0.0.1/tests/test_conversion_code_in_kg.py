import re

import pytest
import tensorflow as tf
import torch

from src.imgdataconvertcodegen.image_data import is_image_equal, get_input_image_and_expected_output
from src.imgdataconvertcodegen.code_generator import ConvertCodeGenerator
from src.imgdataconvertcodegen.knowledge_graph_construction import get_knowledge_graph_constructor


@pytest.fixture(scope="session")
def code_generator():
    constructor = get_knowledge_graph_constructor()
    constructor.build_from_scratch()
    code_generator = ConvertCodeGenerator(constructor.knowledge_graph)
    return code_generator


def assert_exec_of_conversion_code_in_edge(source_metadata, target_metadata, kg):
    edge_data = kg.get_edge_data(source_metadata, target_metadata)
    conversion = edge_data.get('conversion')
    assert conversion is not None, f"No conversion from {source_metadata} to {target_metadata}"
    assert len(conversion) == 2, (f"Expected two elements in the conversions, but got: {conversion} from"
                                  f" {source_metadata} to {target_metadata}")
    assert isinstance(conversion[0], str), (f"Expected the first element of the conversion to be a string, but got:"
                                            f" {conversion[0]} from {source_metadata} to {target_metadata}")
    assert isinstance(conversion[1], str), (f"Expected the second element of the conversion to be a string, but got:"
                                            f" {conversion[1]} from {source_metadata} to {target_metadata}")
    error_message = (f"conversion from\n {source_metadata} to\n {target_metadata} failed\n "
                     f"imports: {conversion[0]}\nconversion function: \n {conversion[1]}\nfrom {edge_data.get('factory')}")

    try:
        source_image, target_image = get_input_image_and_expected_output(source_metadata, target_metadata)
        func_name = re.search(r'(?<=def )\w+', conversion[1]).group(0)

        scope = {}
        scope.update({'source_image': source_image})
        exec(f"""{conversion[0]}
{conversion[1]}
actual_image = {func_name}(source_image)""", scope)
        actual_image = scope.get('actual_image')
    except Exception as e:
        raise AssertionError(f"Failed to execute conversion code from {error_message}") from e

    assert is_image_equal(target_image,
                          actual_image), f'expected {target_image}, but actual {actual_image}. {error_message}'


def is_code_exec_on_cpu(edge):
    return edge[0]['device'] == 'cpu' and edge[1]['device'] == 'cpu'


def test_all_conversion_code_exec_on_cpu(code_generator):
    kg = code_generator.knowledge_graph
    for edge in kg.edges:
        if is_code_exec_on_cpu(edge):
            assert_exec_of_conversion_code_in_edge(*edge, kg)


def is_on_gpu_as_data_repr(edge, data_reprs: list):
    if is_code_exec_on_cpu(edge):
        return False
    return edge[0]['data_representation'] in data_reprs and edge[1]['data_representation'] in data_reprs


def _check_pytorch_gpu_version_installed():
    return torch.version.cuda is not None


def pytorch_gpu_available():
    return torch.cuda.is_available() and _check_pytorch_gpu_version_installed()


def tensorflow_gpu_available():
    return len(tf.config.list_physical_devices('GPU')) > 0


@pytest.mark.skipif(not pytorch_gpu_available(),
                    reason="Test skipped because PyTorch is not installed with CUDA support or"
                           " no CUDA-compatible GPU is available.")
def test_conversion_code_exec_using_pytorch_gpu(code_generator):
    kg = code_generator.knowledge_graph
    for edge in kg.edges:
        if is_on_gpu_as_data_repr(edge, ['torch.tensor']):
            assert_exec_of_conversion_code_in_edge(*edge, kg)


@pytest.mark.skipif(not tensorflow_gpu_available(),
                    reason="Test skipped because TensorFlow not configured for GPU acceleration or"
                           " no CUDA-compatible GPU is available.")
def test_conversion_code_exec_using_tensorflow_gpu(code_generator):
    kg = code_generator.knowledge_graph
    for edge in kg.edges:
        if is_on_gpu_as_data_repr(edge, ['tf.tensor']):
            assert_exec_of_conversion_code_in_edge(*edge, kg)


@pytest.mark.skipif(not tensorflow_gpu_available() or not pytorch_gpu_available(),
                    reason=f"Test skipped because {'TensorFlow' if not tensorflow_gpu_available() else 'Pytorch'} not"
                           f" configured for GPU acceleration or no CUDA-compatible GPU is available.")
def test_conversion_code_exec_using_tensorflow_gpu_torch_gpu(code_generator):
    kg = code_generator.knowledge_graph
    for edge in kg.edges:
        if is_on_gpu_as_data_repr(edge, ['tf.tensor', 'torch.tensor']):
            assert_exec_of_conversion_code_in_edge(*edge, kg)
