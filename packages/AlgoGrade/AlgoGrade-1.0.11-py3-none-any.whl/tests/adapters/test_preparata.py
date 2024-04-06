from pytest import fixture
from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.preparata import PreparataNode, PreparataThreadedBinTree 
from AlgoGrade.adapters import PointPydanticAdapter
from AlgoGrade.preparata import PreparataNodePydanticAdapter, PreparataThreadedBinTreePydanticAdapter


@fixture
def preparata_node_adapter():
    point_adapter = PointPydanticAdapter(coords=(1, 1))
    return PreparataNodePydanticAdapter(data=point_adapter)


@fixture
def preparata_node_regular():
    point = Point(1, 1)
    return PreparataNode(point)


def test_preparata_node_adapter(preparata_node_adapter, preparata_node_regular):
    assert preparata_node_adapter.regular_object() == preparata_node_regular
    assert PreparataNodePydanticAdapter.from_regular_object(preparata_node_regular) == preparata_node_adapter


def test_preparata_node_adapter_serialization(preparata_node_adapter):
    serialized_node = preparata_node_adapter.model_dump()
    deserialized_node = PreparataNodePydanticAdapter(**serialized_node)
    assert deserialized_node.regular_object() == preparata_node_adapter.regular_object()


def test_preparata_tree_adapter(preparata_node_adapter, preparata_node_regular):
    tree_adapter = PreparataThreadedBinTreePydanticAdapter(root=preparata_node_adapter)
    regular_object = PreparataThreadedBinTree(preparata_node_regular)

    assert tree_adapter.regular_object() == regular_object
    assert PreparataThreadedBinTreePydanticAdapter.from_regular_object(regular_object) == tree_adapter


def test_preparata_tree_adapter_serialization(preparata_node_adapter):
    tree_adapter = PreparataThreadedBinTreePydanticAdapter(root=preparata_node_adapter)
    serialized_tree = tree_adapter.model_dump()
    deserialized_tree = PreparataThreadedBinTreePydanticAdapter(**serialized_tree)
    assert deserialized_tree.regular_object().root.data == tree_adapter.regular_object().root.data