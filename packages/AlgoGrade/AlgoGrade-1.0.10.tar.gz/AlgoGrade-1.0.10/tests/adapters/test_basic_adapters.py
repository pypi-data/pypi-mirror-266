from copy import deepcopy
from pytest import fixture
from PyCompGeomAlgorithms.core import Point, BinTreeNode, BinTree, ThreadedBinTreeNode, ThreadedBinTree
from AlgoGrade.adapters import PointPydanticAdapter, BinTreeNodePydanticAdapter, BinTreePydanticAdapter, ThreadedBinTreeNodePydanticAdapter, ThreadedBinTreePydanticAdapter


@fixture
def coords():
    return 1, 2, 3


@fixture
def regular_point(coords):
    return Point(*coords)


@fixture
def adapter_point(coords):
    return PointPydanticAdapter(coords=coords)


def test_point_adapter(regular_point, adapter_point):
    assert adapter_point.regular_object() == regular_point


def test_point_adapter_serialization(adapter_point):
    serialized_point = adapter_point.model_dump()
    deserialized_point = PointPydanticAdapter(**serialized_point)
    assert deserialized_point.regular_object() == adapter_point.regular_object()


@fixture
def adapter_root():
    adapter_root = BinTreeNodePydanticAdapter(data=1)
    adapter_left = BinTreeNodePydanticAdapter(data=2)
    adapter_right = BinTreeNodePydanticAdapter(data=3)
    adapter_root.left = adapter_left
    adapter_root.right = adapter_right

    return adapter_root


@fixture
def regular_root():
    return BinTreeNode(1, left=BinTreeNode(2), right=BinTreeNode(3))


def test_bin_tree_node_adapter(adapter_root, regular_root):
    assert adapter_root.regular_object() == regular_root


def test_bin_tree_node_adapter_serialization(adapter_root):
    serialized_root = adapter_root.model_dump()
    deserialized_root = BinTreeNodePydanticAdapter(**serialized_root)
    assert deserialized_root.regular_object() == adapter_root.regular_object()


def test_bin_tree_adapter(adapter_root, regular_root):
    adapter_tree = BinTreePydanticAdapter(root=adapter_root)
    regular_tree = BinTree(regular_root)
    assert adapter_tree.regular_object() == regular_tree


def test_bin_tree_adapter_serialization(adapter_root):
    adapter_tree = BinTreePydanticAdapter(root=adapter_root)
    serialized_tree = adapter_tree.model_dump()
    deserialized_tree = BinTreePydanticAdapter(**serialized_tree)
    assert deserialized_tree.regular_object() == adapter_tree.regular_object()


@fixture
def adapter_tbt_root_circular():
    adapter_root = ThreadedBinTreeNodePydanticAdapter(data=1)
    adapter_left = ThreadedBinTreeNodePydanticAdapter(data=2)
    adapter_right =ThreadedBinTreeNodePydanticAdapter(data=3)
    adapter_root.left = adapter_left
    adapter_root.right = adapter_right

    adapter_root.prev = adapter_root.left
    adapter_root.next = adapter_root.right
    adapter_left.prev = adapter_right
    adapter_left.next = adapter_root
    adapter_right.prev = adapter_root
    adapter_right.next = adapter_left

    return adapter_root


@fixture
def regular_tbt_root_circular():
    left = ThreadedBinTreeNode(2)
    right = ThreadedBinTreeNode(3)
    root = ThreadedBinTreeNode(1, left, right)
    root.prev = left
    root.next = right
    left.prev = right
    left.next = root
    right.prev = root
    right.next = left

    return root


@fixture
def adapter_tbt_root(adapter_tbt_root_circular):
    adapter_tbt_root = deepcopy(adapter_tbt_root_circular)
    adapter_tbt_root.left.prev = None
    adapter_tbt_root.right.next = None

    return adapter_tbt_root


@fixture
def regular_tbt_root(regular_tbt_root_circular):
    regular_tbt_root = deepcopy(regular_tbt_root_circular)
    regular_tbt_root.left.prev = None
    regular_tbt_root.right.next = None

    return regular_tbt_root


def test_threaded_bin_tree_node_adapter(adapter_tbt_root, regular_tbt_root):
    assert adapter_tbt_root.regular_object() == regular_tbt_root


def test_threaded_bin_tree_node_adapter_circular(adapter_tbt_root_circular, regular_tbt_root_circular):
    assert adapter_tbt_root_circular.regular_object() == regular_tbt_root_circular


def test_threaded_bin_tree_node_adapter_seriaization(adapter_tbt_root):
    serialized_root = adapter_tbt_root.model_dump()
    deserialized_root = ThreadedBinTreeNodePydanticAdapter(**serialized_root)
    assert deserialized_root.regular_object() == adapter_tbt_root.regular_object()


def test_threaded_bin_tree_node_adapter_circular_seriaization(adapter_tbt_root_circular):
    serialized_root = adapter_tbt_root_circular.model_dump()
    deserialized_root = ThreadedBinTreeNodePydanticAdapter(**serialized_root)
    assert deserialized_root.regular_object() == adapter_tbt_root_circular.regular_object()


def test_threaded_bin_tree_adapter(adapter_tbt_root, regular_tbt_root):
    adapter_tbt = ThreadedBinTreePydanticAdapter(root=adapter_tbt_root)
    regular_tbt = ThreadedBinTree(regular_tbt_root)
    assert adapter_tbt.regular_object() == regular_tbt


def test_threaded_bin_tree_adapter_circular(adapter_tbt_root_circular, regular_tbt_root_circular):
    adapter_tbt = ThreadedBinTreePydanticAdapter(root=adapter_tbt_root_circular)
    regular_tbt = ThreadedBinTree(regular_tbt_root_circular)
    assert adapter_tbt.regular_object() == regular_tbt


def test_threaded_bin_tree_adapter_serialization(adapter_tbt_root):
    adapter_tbt = ThreadedBinTreePydanticAdapter(root=adapter_tbt_root)
    serialized_tbt = adapter_tbt.model_dump()
    deserialized_tbt = ThreadedBinTreePydanticAdapter(**serialized_tbt)

    assert deserialized_tbt.regular_object() == adapter_tbt.regular_object()


def test_threaded_bin_tree_adapter_circular_serialization(adapter_tbt_root_circular):
    adapter_tbt = ThreadedBinTreePydanticAdapter(root=adapter_tbt_root_circular)
    serialized_tbt = adapter_tbt.model_dump()
    deserialized_tbt = ThreadedBinTreePydanticAdapter(**serialized_tbt)

    assert deserialized_tbt.regular_object() == adapter_tbt.regular_object()