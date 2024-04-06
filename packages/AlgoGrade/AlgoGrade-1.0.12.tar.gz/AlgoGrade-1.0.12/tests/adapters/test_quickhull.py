from pytest import fixture
from PyCompGeomAlgorithms.core import Point, BinTree
from PyCompGeomAlgorithms.quickhull import QuickhullNode
from AlgoGrade.adapters import PointPydanticAdapter
from AlgoGrade.quickhull import QuickhullNodePydanticAdapter, QuickhullTreePydanticAdapter


@fixture
def regular_node():
    return QuickhullNode([Point(1, 1), Point(2, 2)], subhull=[Point(1, 1), Point(2, 2)])


@fixture
def adapter_node():
    return QuickhullNodePydanticAdapter(
        data=[
            PointPydanticAdapter(coords=(1, 1)),
            PointPydanticAdapter(coords=(2, 2))
        ],
        subhull=[
            PointPydanticAdapter(coords=(1, 1)),
            PointPydanticAdapter(coords=(2, 2))
        ]
    )


def test_quickhull_node_adapter(regular_node, adapter_node):
    assert adapter_node.regular_object() == regular_node
    assert QuickhullNodePydanticAdapter.from_regular_object(regular_node) == adapter_node


def test_quickhull_node_adapter_serialization(adapter_node):
    serialized_node = adapter_node.model_dump()
    deserialized_node = QuickhullNodePydanticAdapter(**serialized_node)
    assert deserialized_node.regular_object() == adapter_node.regular_object()


def test_quickhull_tree_adapter(regular_node, adapter_node):
    regular_object = BinTree(regular_node)
    adapter_object = QuickhullTreePydanticAdapter(root=adapter_node)

    assert adapter_object.regular_object() == regular_object
    assert QuickhullTreePydanticAdapter.from_regular_object(regular_object) == adapter_object


def test_quickhull_tree_adapter_serialization(adapter_node):
    adapter_tree = QuickhullTreePydanticAdapter(root=adapter_node)
    serialized_tree = adapter_tree.model_dump()
    deserialized_tree = QuickhullTreePydanticAdapter(**serialized_tree)
    assert deserialized_tree.regular_object() == adapter_tree.regular_object()