from copy import deepcopy
from math import isclose
from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.graham import GrahamStepsTable, GrahamStepsTableRow
from AlgoGrade.graham import GrahamGrader, GrahamTask, GrahamAnswers
from AlgoGrade.adapters import pycga_to_pydantic
from AlgoGrade.core import Scoring


points = [
    Point(2, 8),
    Point(5, 6),
    Point(7, 8),
    Point(8, 11),
    Point(7, 5),
    Point(10, 7),
    Point(11, 5),
    Point(8, 2),
    Point(1, 3),
    Point(5, 2),
]
givens = (points,)
task_class = GrahamTask
scorings = [
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.15, fine=0.15),
    Scoring(max_grade=0.15, fine=0.15),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.6, fine=0.3, repeat_fine=0.6),
    Scoring(max_grade=0.1, fine=0.25)
]
correct_pycga_answers = task_class.solve_as_pycga_list(givens)
correct_pydantic_answers = task_class.solve_as_pydantic_list(givens)
correct_answers_wrapper = task_class.solve_as_answers_wrapper(givens)


def test_graham_grader_all_correct():
    centroid = Point(4.6667, 7.3333)
    ordered = [
        Point(8, 2),
        Point(7, 5),
        Point(11, 5),
        Point(10, 7),
        Point(7, 8),
        Point(8, 11),
        Point(2, 8),
        Point(1, 3),
        Point(5, 2),
        Point(5, 6)
    ]
    origin = Point(8, 2)
    steps_table = GrahamStepsTable(ordered)
    steps_table.extend([
        GrahamStepsTableRow((ordered[0], ordered[1], ordered[2]), False),
        GrahamStepsTableRow((ordered[0], ordered[2], ordered[3]), True),
        GrahamStepsTableRow((ordered[2], ordered[3], ordered[4]), True),
        GrahamStepsTableRow((ordered[3], ordered[4], ordered[5]), False),
        GrahamStepsTableRow((ordered[2], ordered[3], ordered[5]), False),
        GrahamStepsTableRow((ordered[0], ordered[2], ordered[5]), True),
        GrahamStepsTableRow((ordered[2], ordered[5], ordered[6]), True),
        GrahamStepsTableRow((ordered[5], ordered[6], ordered[7]), True),
        GrahamStepsTableRow((ordered[6], ordered[7], ordered[8]), True),
        GrahamStepsTableRow((ordered[7], ordered[8], ordered[9]), True),
        GrahamStepsTableRow((ordered[8], ordered[9], ordered[0]), False),
        GrahamStepsTableRow((ordered[7], ordered[8], ordered[0]), True)
    ])
    triples = [row.point_triple for row in steps_table]
    are_angles_less_than_pi = [row.is_angle_less_than_pi for row in steps_table]

    pycga_answers = [
        centroid,
        ordered,
        origin,
        triples,
        are_angles_less_than_pi,
        steps_table,
        steps_table,
        steps_table
    ]
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2)


def test_graham_grader_incorrect_centroid():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[0] = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_graham_grader_incorrect_ordered_points():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1] = [
        Point(2000, 2000),
        Point(5000, 5000),
        Point(11, 5),
        Point(10, 7),
        Point(7, 8),
        Point(8, 11),
        Point(2, 8),
        Point(3000, 3000),
        Point(5, 2),
        Point(5, 6)
    ]

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_graham_grader_incorrect_origin():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[2] = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_graham_grader_incorrect_triples():
    pycga_answers = deepcopy(correct_pycga_answers)
    ordered = pycga_answers[1]
    pycga_answers[3] = [
        (ordered[0], ordered[0], ordered[0]),
        (ordered[0], ordered[0], ordered[0]),
        (ordered[2], ordered[3], ordered[4]),
        (ordered[3], ordered[4], ordered[5]),
        (ordered[2], ordered[3], ordered[5]),
        (ordered[0], ordered[2], ordered[5]),
        (ordered[2], ordered[5], ordered[6]),
        (ordered[5], ordered[6], ordered[7]),
        (ordered[6], ordered[7], ordered[8]),
        (ordered[7], ordered[8], ordered[9]),
        (ordered[8], ordered[9], ordered[0]),
        (ordered[7], ordered[8], ordered[0])
    ]

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.85)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.85)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.85)


def test_graham_grader_incorrect_are_angles_less_than_pi():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[4] = [False for _ in pycga_answers[4]]

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.85)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.85)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.85)


def test_graham_grader_incorrect_rows_with_angles_less_than_pi():
    pycga_answers = deepcopy(correct_pycga_answers)
    ordered = pycga_answers[1]
    incorrect_point = Point(1000, 1000)

    pycga_answers[5][7] = GrahamStepsTableRow((ordered[5], ordered[6], incorrect_point), True)
    pycga_answers[5][8] = GrahamStepsTableRow((ordered[6], ordered[7], incorrect_point), True)
    
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_graham_grader_incorrect_rows_with_angles_not_less_than_pi_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    ordered = pycga_answers[1]
    incorrect_point = Point(1000, 1000)

    pycga_answers[5][1] = GrahamStepsTableRow((ordered[0], ordered[2], incorrect_point), True)
    
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.45) # also triggers "rows with angles < pi" grading

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.45)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.45)


def test_graham_grader_incorrect_rows_with_angles_not_less_than_pi_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    incorrect_point = Point(1000, 1000)

    pycga_answers[5][1] = GrahamStepsTableRow((incorrect_point, incorrect_point, incorrect_point), True)
    pycga_answers[5][5] = GrahamStepsTableRow((incorrect_point, incorrect_point, incorrect_point), True)
    
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.15) # also triggers "rows with angles < pi" grading

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.15)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.15)


def test_graham_grader_incorrect_finalization():
    pycga_answers = deepcopy(correct_pycga_answers)
    ordered = pycga_answers[1]
    pycga_answers[6][7] = GrahamStepsTableRow((ordered[5], ordered[0], ordered[7]), True)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = GrahamAnswers.from_iterable(pydantic_answers)

    total_grade, answer_grades = GrahamGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.5) # also triggers "rows with angles < pi" grading

    total_grade, answer_grades = GrahamGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.5)

    total_grade, answer_grades = GrahamGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.5)


