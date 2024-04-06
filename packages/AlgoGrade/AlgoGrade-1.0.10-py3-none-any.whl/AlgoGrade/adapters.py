from __future__ import annotations
from typing import Any, ClassVar, Optional, Iterable, Generator, Union
from enum import Enum
from copy import deepcopy
from typing_extensions import Literal
from pydantic import BaseModel
from PyCompGeomAlgorithms.core import PyCGAObject, Point, BinTreeNode, BinTree, ThreadedBinTreeNode, ThreadedBinTree
from PyCompGeomAlgorithms.dynamic_hull import DynamicHullNode, DynamicHullTree, SubhullNode, SubhullThreadedBinTree
from PyCompGeomAlgorithms.graham import GrahamStepsTableRow, GrahamStepsTable
from PyCompGeomAlgorithms.preparata import PreparataNode, PreparataThreadedBinTree
from PyCompGeomAlgorithms.quickhull import QuickhullNode, QuickhullTree


class SerializablePydanticModelWithPydanticFields(BaseModel):
    """
        A class to ensure correct serialization of Pydantic models that have other Pydantic models' instances as fields
        with possible cyclic references whose custom serialization is specified in those models.
    """
    def model_dump(self, *args, **kwargs):
        tmp_fields_dict = {}
        this_utility_class = SerializablePydanticModelWithPydanticFields

        for field, value in self.__dict__.items():
            tmp_fields_dict[field] = value
            
            if isinstance(value, this_utility_class):
                setattr(self, field, value.model_dump())
            elif isinstance(value, dict):
                setattr(
                    self,
                    field,
                    {
                        (k.model_dump() if isinstance(k, this_utility_class) else k): (v.model_dump() if isinstance(v, this_utility_class) else v)
                        for k, v in value.items()
                    }
                )
            elif not isinstance(value, str) and not isinstance(value, BaseModel) and isinstance(value, Iterable): # BaseModel's are Iterables, but we don't need them to be checked here 
                generator = (item.model_dump() if isinstance(item, this_utility_class) else item for item in value)
                setattr(self, field, generator if isinstance(value, Generator) else value.__class__(generator))
                
        result = super().model_dump(*args, **kwargs)

        for field, value in tmp_fields_dict.items():
            setattr(self, field, value)
        
        return result


class PydanticAdapter(SerializablePydanticModelWithPydanticFields):
    regular_class: ClassVar[type] = object

    @classmethod
    def from_regular_object(cls, obj, **kwargs):
        raise NotImplementedError

    def regular_object(self):
        return self.regular_class(**{
            field: self._regular_object(value)
            for field, value in self.__dict__.items()
        })
    
    @classmethod
    def _regular_object(cls, obj):
        if isinstance(obj, PydanticAdapter):
            return obj.regular_object()
        if isinstance(obj, dict):
            return {cls._regular_object(key): cls._regular_object(value) for key, value in obj.items()}
        if isinstance(obj, Iterable) and not isinstance(obj, str):
            generator = (cls._regular_object(item) for item in obj)
            return generator if isinstance(obj, Generator) else obj.__class__(generator)
        
        return obj

    def __eq__(self, other):
        return self.regular_object() == (other.regular_object() if isinstance(other, self.__class__) else other)
    
    def __hash__(self):
        return hash(self.regular_object())


class PointPydanticAdapter(PydanticAdapter):
    regular_class: ClassVar[type] = Point
    coords: tuple[float, ...]

    @classmethod
    def from_regular_object(cls, obj: Point, **kwargs):
        return cls(coords=obj.coords, **kwargs)

    def regular_object(self):
        return self.regular_class(*self.coords)


class BinTreeNodePydanticAdapter(PydanticAdapter):
    regular_class: ClassVar[type] = BinTreeNode
    data: Any # WARNING: do not leave Any in derived classes, override with specifying that type! (Otherwise it might come out as underserialized portion of JSON when deserializing)
    left: Optional[BinTreeNodePydanticAdapter] = None
    right: Optional[BinTreeNodePydanticAdapter] = None

    @classmethod
    def from_regular_object(cls, obj: BinTreeNode, **kwargs):
        return cls(
            data=pycga_to_pydantic(obj.data),
            left=pycga_to_pydantic(obj.left),
            right=pycga_to_pydantic(obj.right),
            **kwargs
        )
    
    def traverse_inorder(self, node=None, nodes=None):
        if node is None:
            node = self
        if nodes is None:
            nodes = []
        
        if node.left:
            self.traverse_inorder(node.left, nodes)
        
        nodes.append(node)

        if node.right:
            self.traverse_inorder(node.right, nodes)
        
        return nodes


class BinTreePydanticAdapter(PydanticAdapter):
    regular_class: ClassVar[type] = BinTree
    root: BinTreeNodePydanticAdapter

    @classmethod
    def from_regular_object(cls, obj: BinTree, **kwargs):
        return cls(root=pycga_to_pydantic(obj.root), **kwargs)
    
    def traverse_inorder(self):
        return self.root.traverse_inorder() if self.root else []


def serialize_threaded_bin_tree_root_or_tree(root_or_tree: ThreadedBinTreeNodePydanticAdapter | ThreadedBinTreePydanticAdapter, *args, **kwargs):
    """
        Serializes both a threaded bin tree or its root.
    """
    copy = deepcopy(root_or_tree)
    nodes_inorder = copy.traverse_inorder() if isinstance(copy, ThreadedBinTreeNodePydanticAdapter) else copy.root.traverse_inorder()
    is_circular = nodes_inorder and nodes_inorder[0].prev is nodes_inorder[-1]

    # Store node positions in inorder traversal instead of nodes to avoid infinite loops and be able to convert the tree to JSON
    for i, node in enumerate(nodes_inorder):
        node.prev = (i - 1) % len(nodes_inorder)
        node.next = (i + 1) % len(nodes_inorder)
    
    if not is_circular and nodes_inorder:
        nodes_inorder[0].prev = None
        nodes_inorder[-1].next = None

    return copy.model_dump(*args, **(kwargs | {'can_serialize': True}))


def deserialize_threaded_bin_tree_root(root):
    nodes_inorder = root.traverse_inorder()
    is_circular = (
        nodes_inorder
        and nodes_inorder[0].prev is not None
        and nodes_inorder[-1].next is not None
        and (
            (nodes_inorder[-1].next == 0)                     # if the object comes from JSON, this checks the node indices (see serialize_threaded_bin_tree_root)
            if isinstance(nodes_inorder[0].prev, int)
            else (nodes_inorder[0].prev is nodes_inorder[-1]) # if the object comes from Python objects, this checks the nodes 
        )
    )

    for i, node in enumerate(nodes_inorder):
        node.prev = nodes_inorder[i-1]
        node.next = nodes_inorder[(i + 1) % len(nodes_inorder)]
    
    if not is_circular and nodes_inorder:
        nodes_inorder[0].prev = None
        nodes_inorder[-1].next = None


class ThreadedBinTreeNodePydanticAdapter(BinTreeNodePydanticAdapter):
    regular_class: ClassVar[type] = ThreadedBinTreeNode
    left: Optional[ThreadedBinTreeNodePydanticAdapter] = None
    right: Optional[ThreadedBinTreeNodePydanticAdapter] = None
    prev: Optional[Union[ThreadedBinTreeNodePydanticAdapter, int]] = None
    next: Optional[Union[ThreadedBinTreeNodePydanticAdapter, int]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        deserialize_threaded_bin_tree_root(self)  
    
    def model_dump(self, *args, **kwargs):
        if kwargs.get('can_serialize', False):
            kwargs.pop('can_serialize')
            return super().model_dump(*args, **kwargs)
        
        return serialize_threaded_bin_tree_root_or_tree(self, *args, **kwargs)

    def regular_object(self):
        return self.regular_class(
            self.data.regular_object() if isinstance(self.data, PydanticAdapter) else self.data,
            self.left.regular_object() if self.left else None,
            self.right.regular_object() if self.right else None
        )
    
    @classmethod
    def from_regular_object(cls, obj: ThreadedBinTreeNode, **kwargs):
        return super().from_regular_object(obj, prev=None, next=None, **kwargs)
        

class ThreadedBinTreePydanticAdapter(BinTreePydanticAdapter):
    regular_class: ClassVar[type] = ThreadedBinTree
    root: ThreadedBinTreeNodePydanticAdapter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        deserialize_threaded_bin_tree_root(self.root)

    def model_dump(self, *args, **kwargs):
        if kwargs.get('can_serialize', False):
            kwargs.pop('can_serialize')
            return super().model_dump(*args, **kwargs)
        
        return serialize_threaded_bin_tree_root_or_tree(self, *args, **kwargs)

    @classmethod
    def from_regular_object(cls, obj: ThreadedBinTree, **kwargs):
        root = obj.root
        is_circular = root.leftmost_node.prev is root.rightmost_node or root.rightmost_node.next is root.leftmost_node
        root = pycga_to_pydantic(obj.root)
        nodes = root.traverse_inorder()

        for i, node in enumerate(nodes):
            node.prev = node.left if node.left else nodes[i-1]
            node.next = node.right if node.right else nodes[(i+1)%len(nodes)]
        
        if not is_circular and nodes:
            nodes[0].prev = None
            nodes[-1].next = None
        
        return cls(root=root, **kwargs)

    def regular_object(self):
        node = self.root
        while node.next is not None and node.next is not self.root:
            node = node.next
        
        is_circular = node.next is self.root
        regular_root = self.root.regular_object()

        return self.regular_class.from_iterable([node.data for node in regular_root.traverse_inorder()], is_circular)


def pydantic_to_pycga(obj: Any | PydanticAdapter | Iterable):    
    if isinstance(obj, PydanticAdapter):
        return obj.regular_object()

    if isinstance(obj, dict):
        return {pydantic_to_pycga(key): pydantic_to_pycga(value) for key, value in obj.items()}
    
    if isinstance(obj, Iterable) and not isinstance(obj, str):
        generator = (pydantic_to_pycga(obj) for obj in obj)
        return generator if isinstance(obj, Generator) else obj.__class__(generator)
    
    return obj


def pycga_to_pydantic(obj: Any | type | PyCGAObject | Iterable):
    if isinstance(obj, type):
        try:
            from .dynamic_hull import DynamicHullNodePydanticAdapter, DynamicHullTreePydanticAdapter, SubhullNodePydanticAdapter, SubhullThreadedBinTreePydanticAdapter
            from .graham import GrahamStepsTableRowPydanticAdapter, GrahamStepsTablePydanticAdapter
            from .preparata import PreparataNodePydanticAdapter, PreparataThreadedBinTreePydanticAdapter
            from .quickhull import QuickhullNodePydanticAdapter, QuickhullTreePydanticAdapter
            
            return {
                Point: PointPydanticAdapter,
                BinTreeNode: BinTreeNodePydanticAdapter,
                BinTree: BinTreePydanticAdapter,
                ThreadedBinTreeNode: ThreadedBinTreeNodePydanticAdapter,
                ThreadedBinTree: ThreadedBinTreePydanticAdapter,
                DynamicHullNode: DynamicHullNodePydanticAdapter,
                DynamicHullTree: DynamicHullTreePydanticAdapter,
                SubhullNode: SubhullNodePydanticAdapter,
                SubhullThreadedBinTree: SubhullThreadedBinTreePydanticAdapter,
                GrahamStepsTableRow: GrahamStepsTableRowPydanticAdapter,
                GrahamStepsTable: GrahamStepsTablePydanticAdapter,
                PreparataNode: PreparataNodePydanticAdapter,
                PreparataThreadedBinTree: PreparataThreadedBinTreePydanticAdapter,
                QuickhullNode: QuickhullNodePydanticAdapter,
                QuickhullTree: QuickhullTreePydanticAdapter,
            }[obj]
        except KeyError as e:
            raise KeyError("unknown PyCGA type") from e

    if isinstance(obj, PyCGAObject) and not isinstance(obj, Enum):
        return pycga_to_pydantic(obj.__class__).from_regular_object(obj)

    if isinstance(obj, dict):
        return {pycga_to_pydantic(key): pycga_to_pydantic(value) for key, value in obj.items()}
    
    if isinstance(obj, Iterable) and not isinstance(obj, str):
        generator = (pycga_to_pydantic(item) for item in obj)
        return generator if isinstance(obj, Generator) else obj.__class__(generator)
    
    return obj