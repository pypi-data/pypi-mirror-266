from AlgoGrade.adapters import PointPydanticAdapter, pydantic_to_pycga
from AlgoGrade.quickhull import QuickhullAnswers, QuickhullNodePydanticAdapter, QuickhullTreePydanticAdapter


def test_quickhull_answers():
    point = PointPydanticAdapter(coords=(1, 1))
    leftmost_point, rightmost_point = point, point
    subset1, subset2 = [point], [point]
    tree = QuickhullTreePydanticAdapter(root=QuickhullNodePydanticAdapter(data=[point]))

    answers_model = QuickhullAnswers(
        leftmost_point=leftmost_point, rightmost_point=rightmost_point,
        subset1=subset1, subset2=subset2, tree=tree
    )
    answers_list = [(leftmost_point, rightmost_point, subset1, subset2), tree, tree, tree, tree]

    assert answers_model.to_pydantic_list() == answers_list
    assert answers_model.to_pycga_list() == pydantic_to_pycga(answers_list)
    assert QuickhullAnswers.from_iterable(answers_list) == answers_model
    assert QuickhullAnswers(**answers_model.model_dump()) == answers_model
