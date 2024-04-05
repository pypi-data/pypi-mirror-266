from typing import ClassVar
from PyCompGeomAlgorithms.graham import graham, GrahamStepsTableRow, GrahamStepsTable
from .adapters import pycga_to_pydantic, pydantic_to_pycga, PydanticAdapter, PointPydanticAdapter
from .core import Task, Grader, Mistake, Answers
from .parsers import PointListGivenJSONParser


class GrahamGrader(Grader):
    @classmethod
    def grade_methods(cls):
        return [
            cls.grade_default,
            cls.grade_iterable,
            cls.grade_default,
            cls.grade_iterable,
            cls.grade_iterable,
            cls.grade_angles_less_than_pi,
            cls.grade_angles_greater_than_or_equal_to_pi,
            cls.grade_finalization
        ]
    
    @classmethod
    def grade_angles_less_than_pi(cls, answer, correct_answer, scorings):
        return [
            Mistake(scorings)
            for row, next_row in zip(answer, answer[1:])
            if row.is_angle_less_than_pi and (
                row.point_triple[1] != next_row.point_triple[0] or
                row.point_triple[2] != next_row.point_triple[1] or
                next_row.point_triple[2] != cls._next_point(answer.ordered_points, row.point_triple[2])
            )
        ]
    
    @classmethod
    def grade_angles_greater_than_or_equal_to_pi(cls, answer, correct_answer, scorings):
        return [
            Mistake(scorings)
            for row, next_row in zip(answer, answer[1:])
            if not row.is_angle_less_than_pi and (
                (
                    row.point_triple[0] != next_row.point_triple[0] or
                    row.point_triple[2] != next_row.point_triple[1] or
                    next_row.point_triple[2] != cls._next_point(answer.ordered_points, next_row.point_triple[1])
                ) if row.point_triple[0] == answer.ordered_points[0] else
                (
                    row.point_triple[0] != next_row.point_triple[1] or
                    row.point_triple[2] != next_row.point_triple[2] or
                    next_row.point_triple[0] != cls._prev_point(answer.rows, next_row)
                )
            )
        ]

    @classmethod
    def grade_finalization(cls, answer, correct_answer, scorings):
        return [
            Mistake(scorings)
            for row in answer
            if row.point_triple[1] == answer.ordered_points[0]
        ]
    
    @staticmethod
    def _prev_point(rows, row):
        i = rows.index(row)

        try:
            return next(r for r in reversed(rows[:i]) if r.point_triple[1] == row.point_triple[1]).point_triple[0]
        except StopIteration:
            return None
    
    @staticmethod
    def _next_point(ordered_points, point):
        try:
            return ordered_points[(ordered_points.index(point)+1) % len(ordered_points)]
        except (IndexError, ValueError):
            return None


class GrahamStepsTableRowPydanticAdapter(PydanticAdapter):
    regular_class: ClassVar[type] = GrahamStepsTableRow
    point_triple: tuple[PointPydanticAdapter, PointPydanticAdapter, PointPydanticAdapter]
    is_angle_less_than_pi: bool

    @classmethod
    def from_regular_object(cls, obj: GrahamStepsTableRow, **kwargs):
        return cls(
            point_triple=pycga_to_pydantic(obj.point_triple),
            is_angle_less_than_pi=obj.is_angle_less_than_pi,
            **kwargs
        )


class GrahamStepsTablePydanticAdapter(PydanticAdapter):
    regular_class: ClassVar[type] = GrahamStepsTable
    ordered_points: list[PointPydanticAdapter]
    rows: list[GrahamStepsTableRowPydanticAdapter]

    @classmethod
    def from_regular_object(cls, obj: GrahamStepsTable, **kwargs):
        return cls(
            ordered_points=pycga_to_pydantic(obj.ordered_points),
            rows=pycga_to_pydantic(obj.rows),
            **kwargs
        )


class GrahamAnswers(Answers):
    centroid: PointPydanticAdapter
    ordered_points: list[PointPydanticAdapter]
    origin: PointPydanticAdapter
    steps_table: GrahamStepsTablePydanticAdapter
    point_triples_: list[tuple[PointPydanticAdapter, PointPydanticAdapter, PointPydanticAdapter]] | None = None
    are_angles_less_than_pi_: list[bool] | None = None

    @classmethod
    def from_iterable(cls, iterable):
        centroid, ordered_points, origin, point_triples, are_angles_less_than_pi, steps_table, *rest = iterable        
        return cls(centroid=centroid, ordered_points=ordered_points, origin=origin, steps_table=steps_table, point_triples_=point_triples, are_angles_less_than_pi_=are_angles_less_than_pi)

    @property
    def point_triples(self):
        return self.point_triples_ or [row.point_triple for row in self.steps_table.rows]

    @property
    def are_angles_less_than_pi(self):
        return self.are_angles_less_than_pi_ or [row.is_angle_less_than_pi for row in self.steps_table.rows]

    def to_pydantic_list(self):
        return [
            self.centroid, self.ordered_points, self.origin, self.point_triples,
            self.are_angles_less_than_pi, self.steps_table, self.steps_table, self.steps_table
        ]
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            tmp_triples = other.point_triples_
            tmp_angles = other.are_angles_less_than_pi_

            other.point_triples_ = self.point_triples_
            other.are_angles_less_than_pi_ = self.are_angles_less_than_pi_

            are_equal = super().__eq__(other)

            other.point_triples_ = tmp_triples
            other.are_angles_less_than_pi_ = tmp_angles

            return are_equal

        return False


class GrahamTask(Task):
    algorithm = graham
    grader_class = GrahamGrader
    answers_class = GrahamAnswers
    given_parser_class = PointListGivenJSONParser
