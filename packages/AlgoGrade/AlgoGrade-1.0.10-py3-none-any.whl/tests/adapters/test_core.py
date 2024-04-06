from copy import deepcopy
from pytest import fixture
from PyCompGeomAlgorithms.core import Point, BinTreeNode, BinTree, ThreadedBinTreeNode, ThreadedBinTree
from AlgoGrade.adapters import PointPydanticAdapter, BinTreeNodePydanticAdapter, BinTreePydanticAdapter, ThreadedBinTreeNodePydanticAdapter, ThreadedBinTreePydanticAdapter


def test_point_adapter():
    coords = 1, 2, 3
    adapter = PointPydanticAdapter(coords=coords)
    regular = Point(*coords)
    assert adapter.regular_object == regular


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
    assert adapter_root.regular_object == regular_root


def test_bin_tree_adapter(adapter_root, regular_root):
    adapter_tree = BinTreePydanticAdapter(root=adapter_root)
    regular_tree = BinTree(regular_root)
    assert adapter_tree.regular_object == regular_tree


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
    assert adapter_tbt_root.regular_object == regular_tbt_root


def test_threaded_bin_tree_adapter(adapter_tbt_root, regular_tbt_root):
    adapter_tbt = ThreadedBinTreePydanticAdapter(root=adapter_tbt_root)
    regular_tbt = ThreadedBinTree(regular_tbt_root)
    assert adapter_tbt.regular_object == regular_tbt


def test_threaded_bin_tree_node_adapter_circular(adapter_tbt_root_circular, regular_tbt_root_circular):
    assert adapter_tbt_root_circular.regular_object == regular_tbt_root_circular


def test_threaded_bin_tree_adapter_circular(adapter_tbt_root_circular, regular_tbt_root_circular):
    adapter_tbt = ThreadedBinTreePydanticAdapter(root=adapter_tbt_root_circular)
    regular_tbt = ThreadedBinTree(regular_tbt_root_circular)
    assert adapter_tbt.regular_object == regular_tbt
