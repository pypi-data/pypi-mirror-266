from __future__ import annotations
from functools import partial
from typing import ClassVar, Optional, Union
from PyCompGeomAlgorithms.core import BinTree
from PyCompGeomAlgorithms.quickhull import quickhull, QuickhullNode
from .adapters import pycga_to_pydantic, PointPydanticAdapter, BinTreeNodePydanticAdapter, BinTreePydanticAdapter
from .core import Task, Grader, Mistake, Answers
from .parsers import PointListGivenJSONParser


class QuickhullGrader(Grader):
    @classmethod
    def grade_methods(cls):
        return [
            cls.grade_iterable,
            partial(cls.grade_bin_tree, grade_item_method=lambda a, c, gp: cls.grade_default(a.h, c.h, gp)),
            partial(cls.grade_bin_tree, grade_item_method=lambda a, c, gp: cls.grade_iterable(a.points, c.points, gp)),
            cls.grade_finalization,
            partial(cls.grade_bin_tree, grade_item_method=lambda a, c, gp: cls.grade_iterable(a.subhull, c.subhull, gp))
        ]
    
    @classmethod
    def grade_finalization(cls, answer, correct_answer, scorings):
        return [Mistake(scorings) for node in answer.traverse_preorder() if not node.is_leaf and len(node.points) == 2]


class QuickhullNodePydanticAdapter(BinTreeNodePydanticAdapter):
    regular_class: ClassVar[type] = QuickhullNode
    data: list[PointPydanticAdapter]
    left: Optional[QuickhullNodePydanticAdapter] = None
    right: Optional[QuickhullNodePydanticAdapter] = None
    h: Optional[PointPydanticAdapter] = None
    subhull: Optional[list[PointPydanticAdapter]] = None

    @classmethod
    def from_regular_object(cls, obj: QuickhullNode, **kwargs):
        return super().from_regular_object(
            obj,
            h=pycga_to_pydantic(obj.h),
            subhull=pycga_to_pydantic(obj.subhull),
            **kwargs
        )


class QuickhullTreePydanticAdapter(BinTreePydanticAdapter):
    regular_class: ClassVar[type] = BinTree
    root: QuickhullNodePydanticAdapter


class QuickhullAnswers(Answers):
    leftmost_point: PointPydanticAdapter
    rightmost_point: PointPydanticAdapter
    subset1: list[PointPydanticAdapter]
    subset2: list[PointPydanticAdapter]
    tree: QuickhullTreePydanticAdapter

    @classmethod
    def from_iterable(cls, iterable):
        (leftmost_point, rightmost_point, subset1, subset2), tree, *rest = iterable
        return cls(
            leftmost_point=leftmost_point, rightmost_point=rightmost_point,
            subset1=subset1, subset2=subset2, tree=tree
        )
    
    def to_pydantic_list(self):
        return [
            (self.leftmost_point, self.rightmost_point, self.subset1, self.subset2),
            self.tree, self.tree, self.tree, self.tree
        ]


class QuickhullTask(Task):
    algorithm = quickhull
    grader_class = QuickhullGrader
    answers_class = QuickhullAnswers
    given_parser_class = PointListGivenJSONParser