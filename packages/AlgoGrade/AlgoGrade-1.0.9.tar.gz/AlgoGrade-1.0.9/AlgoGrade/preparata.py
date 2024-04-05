from __future__ import annotations
from functools import partial
from typing import ClassVar, Optional
from PyCompGeomAlgorithms.core import ThreadedBinTree
from PyCompGeomAlgorithms.preparata import preparata, PreparataNode, PreparataThreadedBinTree
from .core import Task, Grader, Answers
from .adapters import PointPydanticAdapter, ThreadedBinTreeNodePydanticAdapter, ThreadedBinTreePydanticAdapter
from .parsers import PointListGivenJSONParser


class PreparataGrader(Grader):
    @classmethod
    def grade_methods(cls):
        return [
            cls.grade_iterable,
            partial(cls.grade_iterable, grade_item_method=partial(cls.grade_iterable, grade_item_method=cls.grade_iterable)),
            partial(cls.grade_iterable, grade_item_method=cls.grade_iterable),
            partial(cls.grade_iterable, grade_item_method=(cls.grade_iterable, partial(cls.grade_iterable, grade_item_method=cls.grade_bin_tree)))
        ]


class PreparataNodePydanticAdapter(ThreadedBinTreeNodePydanticAdapter):
    regular_class: ClassVar[type] = PreparataNode
    data: PointPydanticAdapter
    left: Optional[PreparataNodePydanticAdapter] = None
    right: Optional[PreparataNodePydanticAdapter] = None

    @classmethod
    def from_regular_object(cls, obj: PreparataNode, **kwargs):
        return super().from_regular_object(obj, **kwargs)


class PreparataThreadedBinTreePydanticAdapter(ThreadedBinTreePydanticAdapter):
    regular_class: ClassVar[type] = PreparataThreadedBinTree
    root: PreparataNodePydanticAdapter

    @classmethod
    def from_regular_object(cls, obj: PreparataThreadedBinTree, **kwargs):
        return super().from_regular_object(obj, **kwargs)


class PreparataAnswers(Answers):
    hull: list[PointPydanticAdapter]
    tree: PreparataThreadedBinTreePydanticAdapter
    left_paths: list[list[PointPydanticAdapter]]
    right_paths: list[list[PointPydanticAdapter]]
    deleted_points_lists: list[list[PointPydanticAdapter]]
    hulls: list[list[PointPydanticAdapter]]
    trees: list[PreparataThreadedBinTreePydanticAdapter]

    @classmethod
    def from_iterable(cls, iterable):
        (hull, tree), (left_paths, right_paths), deleted_points_lists, (hulls, trees), *rest = iterable
        return cls(
            hull=hull, tree=tree, left_paths=left_paths, right_paths=right_paths,
            deleted_points_lists=deleted_points_lists, hulls=hulls, trees=trees
        )
    
    def to_pydantic_list(self):
        return [
            (self.hull, self.tree), (self.left_paths, self.right_paths),
            self.deleted_points_lists, (self.hulls, self.trees)
        ]


class PreparataTask(Task):
    algorithm = preparata
    grader_class = PreparataGrader
    answers_class = PreparataAnswers
    given_parser_class = PointListGivenJSONParser
