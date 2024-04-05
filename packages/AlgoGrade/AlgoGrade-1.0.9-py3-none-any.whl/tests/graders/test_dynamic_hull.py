from math import isclose
from copy import deepcopy
from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.dynamic_hull import DynamicHullNode, DynamicHullTree, SubhullThreadedBinTree, PathDirection
from AlgoGrade.dynamic_hull import DynamicHullTask, DynamicHullGrader, DynamicHullAnswers
from AlgoGrade.adapters import pycga_to_pydantic
from AlgoGrade.core import Scoring


points = p2, p1, p3 = [Point(3, 3), Point(1, 1), Point(5, 0)]
point_to_insert = Point(4, 3)
givens = points, point_to_insert
task_class = DynamicHullTask
scorings = [
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.5, fine=0.25, repeat_fine=0.5),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.5, fine=0.25, repeat_fine=0.5),
    Scoring(max_grade=0.25, fine=0.25, repeat_fine=0.5),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.25, fine=0.25),
    Scoring(max_grade=0.75, fine=0.25, repeat_fine=0.75)
]
correct_pycga_answers = task_class.solve_as_pycga_list(givens)
correct_pydantic_answers = task_class.solve_as_pydantic_list(givens)
correct_answers_wrapper = task_class.solve_as_answers_wrapper(givens)


def test_dynamic_hull_grader_all_correct():
    root = DynamicHullNode(p2, [p1, p2, p3], 1)
    root.left = DynamicHullNode(p1, [p1, p2])
    root.left.left = DynamicHullNode.leaf(p1)
    root.left.right = DynamicHullNode.leaf(p2)
    root.right = DynamicHullNode.leaf(p3)
    tree = DynamicHullTree(root)
    
    optimized_tree = deepcopy(tree)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.left.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.left.left.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.left.right.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.right.optimized_subhull = SubhullThreadedBinTree.empty()
    
    leaves = [root.left.left, root.left.right, root.right]
    path = [PathDirection.right]
    hull = [p1, p2, point_to_insert, p3]

    optimized_tree2 = deepcopy(optimized_tree)
    optimized_tree2.root.subhull = SubhullThreadedBinTree.from_iterable(hull)
    optimized_tree2.root.optimized_subhull = optimized_tree2.root.subhull
    optimized_tree2.root.right = DynamicHullNode(point_to_insert, [point_to_insert, p3])
    optimized_tree2.root.right.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree2.root.right.left = DynamicHullNode.leaf(point_to_insert)
    optimized_tree2.root.right.left.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree2.root.right.right = DynamicHullNode.leaf(p3)
    optimized_tree2.root.right.right.optimized_subhull = SubhullThreadedBinTree.empty()

    pycga_answers = [
        leaves,
        tree,
        tree,
        tree,
        tree,
        optimized_tree,
        path,
        (optimized_tree2, hull)
    ]
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 3)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 3)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 3)


def test_dynamic_hull_grader_incorrect_leaves():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[0] = deepcopy(pycga_answers[0])
    leaves = pycga_answers[0]
    leaves[0].data = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_left_supporting_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.left_supporting = Point(100, 100) # also triggers "omitted points" grading

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.5)



def test_dynamic_hull_grader_incorrect_right_supporting_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.right_supporting = Point(100, 100) # also triggers "omitted points" grading

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.5)


def test_dynamic_hull_grader_incorrect_left_and_right_supporting():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.left_supporting = Point(100, 100)  # also triggers "omitted points" grading
    pycga_answers[1].root.right_supporting = Point(100, 100) # also triggers "omitted points" grading

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.25)


def test_dynamic_hull_grader_incorrect_left_supporting_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.left_supporting = Point(100, 100) # also triggers "omitted points" grading
    pycga_answers[1].root.left.left_supporting = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.25)


def test_dynamic_hull_grader_incorrect_right_supporting_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[1].root.right_supporting = Point(100, 100) # also triggers "omitted points" grading
    pycga_answers[1].root.left.right_supporting = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.25)


def test_dynamic_hull_grader_incorrect_omitted_points2():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[2].root.subhull = SubhullThreadedBinTree.from_iterable([Point(0, 0)] *3)
    
    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 1.75) # also triggers supporting points and subhull grading

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 1.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 1.75)


def test_dynamic_hull_grader_incorrect_subhull_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[3].root.left_supporting = pycga_answers[2].root.left_supporting
    pycga_answers[3].root.right_supporting = pycga_answers[2].root.right_supporting
    pycga_answers[3].root.subhull.root.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_subhull_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[3].root.left_supporting = pycga_answers[2].root.left_supporting
    pycga_answers[3].root.right_supporting = pycga_answers[2].root.right_supporting
    pycga_answers[3].root.subhull.root.point = Point(100, 100)

    pycga_answers[3].root.left.left_supporting = pycga_answers[2].root.left.left_supporting
    pycga_answers[3].root.left.right_supporting = pycga_answers[2].root.left.right_supporting
    pycga_answers[3].root.left.subhull.root.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.5)


def test_dynamic_hull_grader_incorrect_point_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[4].root.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_point_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[4].root.point = Point(100, 100)
    pycga_answers[4].root.left.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.5)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.5)


def test_dynamic_hull_grader_incorrect_optimization():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[5].root.optimized_subhull.root.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_search_path():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[6][0] = PathDirection.left

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_final_tree_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[7][0].root.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_final_hull_single():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[7][1][0] = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.75)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.75)


def test_dynamic_hull_grader_incorrect_final_tree_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[7][0].root.point = Point(100, 100)
    pycga_answers[7][0].root.left.point = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.25)


def test_dynamic_hull_grader_incorrect_final_hull_repeated():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[7][1][0] = Point(100, 100)
    pycga_answers[7][1][1] = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.25)


def test_dynamic_hull_grader_incorrect_final_tree_and_hull():
    pycga_answers = deepcopy(correct_pycga_answers)
    pycga_answers[7][0].root.point = Point(100, 100)
    pycga_answers[7][1][0] = Point(100, 100)

    pydantic_answers = pycga_to_pydantic(pycga_answers)
    answers_wrapper = DynamicHullAnswers.from_iterable(pydantic_answers)

    total_grade, answers_grades = DynamicHullGrader.grade_pycga(pycga_answers, correct_pycga_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_pydantic(pydantic_answers, correct_pydantic_answers, scorings)
    assert isclose(total_grade, 2.25)

    total_grade, answers_grades = DynamicHullGrader.grade_answers_wrapper(answers_wrapper, correct_answers_wrapper, scorings)
    assert isclose(total_grade, 2.25)