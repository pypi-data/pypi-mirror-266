from PyCompGeomAlgorithms.core import Point
from AlgoGrade.adapters import pycga_to_pydantic, pydantic_to_pycga, PointPydanticAdapter


def test_pycga_to_pydantic_type():
    assert pycga_to_pydantic(Point) == PointPydanticAdapter


def test_interlibrary_converters_pycga_object():
    point_pycga = Point(1, 2)
    point_adapter = PointPydanticAdapter(coords=(1, 2))

    assert pycga_to_pydantic(point_pycga) == point_adapter
    assert pydantic_to_pycga(point_adapter) == point_pycga


def test_interlibrary_converters_flat_dict():
    flat_dict_pycga = {Point(1, 2): 1, 42: "a", Point(3): 3, "abc": 1}
    flat_dict_adapter = {
        PointPydanticAdapter(coords=(1, 2)): 1,
        42: "a",
        PointPydanticAdapter(coords=(3,)): 3,
        "abc": 1
    }

    assert pycga_to_pydantic(flat_dict_pycga) == flat_dict_adapter
    assert pydantic_to_pycga(flat_dict_adapter) == flat_dict_pycga


def test_interlibrary_converters_nested_dict():
    nested_dict_pycga = {
        Point(1, 2): {1: 2, "abc": Point(3, 3), 42: {}},
        2: 2,
        "a": {Point(6, 5), 7}
    }
    nested_dict_adapter = {
        PointPydanticAdapter(coords=(1, 2)): {1: 2, "abc": PointPydanticAdapter(coords=(3, 3)), 42: {}},
        2: 2,
        "a": {PointPydanticAdapter(coords=(6, 5)), 7}
    }

    assert pycga_to_pydantic(nested_dict_pycga) == nested_dict_adapter
    assert pydantic_to_pycga(nested_dict_adapter) == nested_dict_pycga


def test_interlibrary_converters_flat_list():
    flat_list_pycga = [Point(1, 2), 42, Point(3), "abc"]
    flat_list_adapter = [PointPydanticAdapter(coords=(1, 2)), 42, PointPydanticAdapter(coords=(3,)), "abc"]

    assert pycga_to_pydantic(flat_list_pycga) == flat_list_adapter
    assert pydantic_to_pycga(flat_list_adapter) == flat_list_pycga


def test_interlibrary_converters_nested_list():
    nested_list_pycga = [
        {1: 2, "abc": Point(3, 3), 42: {}},
        2,
        [Point(6, 5), 7, []]
    ]
    nested_list_adapter = [
        {1: 2, "abc": PointPydanticAdapter(coords=(3, 3)), 42: {}},
        2,
        [PointPydanticAdapter(coords=(6, 5)), 7, []]
    ]

    assert pycga_to_pydantic(nested_list_pycga) == nested_list_adapter
    assert pydantic_to_pycga(nested_list_adapter) == nested_list_pycga
