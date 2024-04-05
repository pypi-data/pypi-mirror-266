from typing import Any
from AlgoGrade.core import Scoring, Grader, Answers
from AlgoGrade.adapters import pycga_to_pydantic


class MockGrader(Grader):
    @classmethod
    def grade_methods(cls):
        return [
            cls.grade_default,
            cls.grade_default,
            cls.grade_iterable   
        ]


class MockAnswers(Answers):
    list: list[Any]

    @classmethod
    def from_iterable(cls, iterable):
        return cls(list=iterable)
    
    def to_pydantic_list(self):
        return self.list


scorings = [
    Scoring(max_grade=10, fine=5),
    Scoring(max_grade=10, fine=5),
    Scoring(min_grade=2, max_grade=10, fine=5, repeat_fine=7)
]


def test_grader1():
    pycga_answers = [1, 2, (3, 4)]
    correct_pycga_answers = pycga_answers

    total_grade, answer_grades = MockGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert total_grade == 30
    assert answer_grades == [(1, 10), (2, 10), ((3, 4), 10)]

    total_grade, answer_grades = MockGrader.grade_pydantic(pycga_to_pydantic(pycga_answers), pycga_to_pydantic(correct_pycga_answers), scorings)
    assert total_grade == 30
    assert answer_grades == [(1, 10), (2, 10), ((3, 4), 10)]

    total_grade, answer_grades = MockGrader.grade_answers_wrapper(
        MockAnswers.from_iterable(pycga_answers),
        MockAnswers.from_iterable(correct_pycga_answers),
        scorings
    )
    assert total_grade == 30
    assert answer_grades == [(1, 10), (2, 10), ((3, 4), 10)]


def test_grader2():
    pycga_answers = [1, 2, (3, 4)]
    correct_pycga_answers = [1, 3, (3, 4)]

    total_grade, answer_grades = MockGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert total_grade == 25
    assert answer_grades == [(1, 10), (2, 5), ((3, 4), 10)]

    total_grade, answer_grades = MockGrader.grade_pydantic(pycga_to_pydantic(pycga_answers), pycga_to_pydantic(correct_pycga_answers), scorings)
    assert total_grade == 25
    assert answer_grades == [(1, 10), (2, 5), ((3, 4), 10)]

    total_grade, answer_grades = MockGrader.grade_answers_wrapper(
        MockAnswers.from_iterable(pycga_answers),
        MockAnswers.from_iterable(correct_pycga_answers),
        scorings
    )
    assert total_grade == 25
    assert answer_grades == [(1, 10), (2, 5), ((3, 4), 10)]


def test_grader3():
    pycga_answers = [1, 2, (3, 4)]
    correct_pycga_answers = [1, 2, (0, 0)]

    total_grade, answer_grades = MockGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert total_grade == 23
    assert answer_grades == [(1, 10), (2, 10), ((3, 4), 3)]

    total_grade, answer_grades = MockGrader.grade_pydantic(pycga_to_pydantic(pycga_answers), pycga_to_pydantic(correct_pycga_answers), scorings)
    assert total_grade == 23
    assert answer_grades == [(1, 10), (2, 10), ((3, 4), 3)]

    total_grade, answer_grades = MockGrader.grade_answers_wrapper(
        MockAnswers.from_iterable(pycga_answers),
        MockAnswers.from_iterable(correct_pycga_answers),
        scorings
    )
    assert total_grade == 23
    assert answer_grades == [(1, 10), (2, 10), ((3, 4), 3)]
