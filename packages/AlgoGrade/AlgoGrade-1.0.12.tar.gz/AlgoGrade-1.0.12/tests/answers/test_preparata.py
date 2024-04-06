from AlgoGrade.adapters import PointPydanticAdapter, pydantic_to_pycga
from AlgoGrade.preparata import PreparataNodePydanticAdapter, PreparataThreadedBinTreePydanticAdapter, PreparataAnswers


def test_preparata_answers():
    point = PointPydanticAdapter(coords=(1, 1))
    hull = [point]
    tree = PreparataThreadedBinTreePydanticAdapter(root=PreparataNodePydanticAdapter(data=point))
    left_paths, right_paths = [[point]], [[point]]
    deleted_points = []
    hulls, trees = [hull], [tree]

    answers_model = PreparataAnswers(
        hull=hull, tree=tree, left_paths=left_paths, right_paths=right_paths,
        deleted_points_lists=deleted_points, hulls=hulls, trees=trees
    )
    answers_list = [(hull, tree), (left_paths, right_paths), deleted_points, (hulls, trees)]

    assert answers_model.to_pydantic_list() == answers_list
    assert answers_model.to_pycga_list() == pydantic_to_pycga(answers_list)
    assert PreparataAnswers.from_iterable(answers_list) == answers_model
    assert PreparataAnswers(**answers_model.model_dump()) == answers_model
