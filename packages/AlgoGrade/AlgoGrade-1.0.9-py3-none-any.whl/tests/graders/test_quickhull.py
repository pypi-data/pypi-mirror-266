from math import isclose
from copy import deepcopy
from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.quickhull import QuickhullNode, QuickhullTree
from AlgoGrade.quickhull import QuickhullGrader, QuickhullTask, QuickhullAnswers
from AlgoGrade.adapters import pycga_to_pydantic
from AlgoGrade.core import Scoring


points = [
    Point(0, 6),
    Point(8, 11),
    Point(10, 4),
    Point(7, 13),
    Point(6, 3),
    Point(3, 0),
    Point(4, 2),
    Point(12, 1),
    Point(14, 10),
    Point(5, 9),
    Point(3, 11),
    Point(1, 4),
]
givens = (points,)
hull = [points[0], points[10], points[3], points[8], points[7], points[5]]
task_class = QuickhullTask
scorings = [
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.25, fine=0.25, repeat_fine=0.5),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=1, fine=1)
]
correct_pycga_answers = task_class.solve_as_pycga_list(givens)
correct_pydantic_answers = task_class.solve_as_pydantic_list(givens)
correct_answers_wrapper = task_class.solve_as_answers_wrapper(givens)


def test_quickhull_grader_all_correct():
    tree = QuickhullTree(
        QuickhullNode(
            [
                points[0],
                points[10],
                points[9],
                points[3],
                points[1],
                points[8],
                points[7],
                points[2],
                points[4],
                points[6],
                points[5],
                points[11],
            ],
            subhull=hull
        )
    )

    tree.root.left = QuickhullNode(
        [points[0], points[10], points[9], points[3], points[1], points[8]],
        h=points[3],
        subhull=[points[0], points[10], points[3], points[8]]
    )
    tree.root.right = QuickhullNode(
        [points[8], points[7], points[2], points[4], points[6], points[5], points[11], points[0]],
        h=points[7],
        subhull=[points[8], points[7], points[5], points[0]]
    )

    tree.root.left.left = QuickhullNode([points[0], points[10], points[3]], h=points[10], subhull=[points[0], points[10], points[3]])
    tree.root.left.right = QuickhullNode([points[3], points[8]], subhull=[points[3], points[8]])
    tree.root.left.left.left = QuickhullNode([points[0], points[10]], subhull=[points[0], points[10]])
    tree.root.left.left.right = QuickhullNode([points[10], points[3]], subhull=[points[10], points[3]])

    tree.root.right.left = QuickhullNode([points[8], points[7]], subhull=[points[8], points[7]])
    tree.root.right.right = QuickhullNode(
        [points[7], points[4], points[6], points[5], points[11], points[0]],
        h=points[5],
        subhull=[points[7], points[5], points[0]]
    )
    tree.root.right.right.left = QuickhullNode([points[7], points[5]], subhull=[points[7], points[5]])
    tree.root.right.right.right = QuickhullNode([points[5], points[0]], subhull=[points[5], points[0]])

    leftmost_point, rightmost_point = points[0], points[8]
    s1, s2 = tree.root.left.points, tree.root.right.points

    pycga_answers = [(leftmost_point, rightmost_point, s1, s2), tree, tree, tree, tree]
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2)


def test_quickhull_grader_incorrect_first_step():
    pycga_answers = deepcopy(correct_pycga_answers)
    first_step_list = list(pycga_answers[0])
    first_step_list[0] = Point(100, 100)
    pycga_answers[0] = tuple(first_step_list)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_quickhull_grader_incorrect_h_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.h = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_quickhull_grader_incorrect_h_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.h = Point(100, 100)
    pycga_answers[1].root.left.h = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.5)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.5)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.5)


def test_quickhull_grader_incorrect_points():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[2].root.left.left.points[0] = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_quickhull_grader_incorrect_finalization():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[3].root.left.right.left = QuickhullNode([]) # leaf node w/ 2 points is now not a leaf

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_quickhull_grader_incorrect_merge():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[4].root.left.right.subhull = [Point(100, 100)]

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = QuickhullAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = QuickhullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1)

    total_grade, answer_grades = QuickhullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1)

    total_grade, answer_grades = QuickhullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1)
