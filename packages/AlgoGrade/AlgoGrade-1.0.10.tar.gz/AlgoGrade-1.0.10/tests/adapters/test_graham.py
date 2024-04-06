from pytest import fixture
from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.graham import GrahamStepsTableRow, GrahamStepsTable
from AlgoGrade.adapters import PointPydanticAdapter
from AlgoGrade.graham import GrahamStepsTableRowPydanticAdapter, GrahamStepsTablePydanticAdapter


@fixture
def table_row_adapter():
    return GrahamStepsTableRowPydanticAdapter(
        point_triple=(
            PointPydanticAdapter(coords=(1, 1)),
            PointPydanticAdapter(coords=(2, 2)),
            PointPydanticAdapter(coords=(3, 3))
        ),
        is_angle_less_than_pi=True
    )


@fixture
def table_adapter(table_row_adapter):
    return GrahamStepsTablePydanticAdapter(
        ordered_points=[PointPydanticAdapter(coords=(1, 1))],
        rows=[table_row_adapter]
    )


def test_steps_table_row_adapter(table_row_adapter):
    regular_object = GrahamStepsTableRow((Point(1, 1), Point(2, 2), Point(3, 3)), True)

    assert table_row_adapter.regular_object() == regular_object
    assert GrahamStepsTableRowPydanticAdapter.from_regular_object(regular_object) == table_row_adapter


def test_steps_table_row_adapter_serializaion(table_row_adapter):
    serialized_row = table_row_adapter.model_dump()
    deserialized_row = GrahamStepsTableRowPydanticAdapter(**serialized_row)
    assert deserialized_row.regular_object() == table_row_adapter.regular_object()


def test_steps_table_adapter(table_adapter):
    regular_object = GrahamStepsTable(
        [Point(1, 1)],
        [GrahamStepsTableRow((Point(1, 1), Point(2, 2), Point(3, 3)), True)]
    )

    assert table_adapter.regular_object() == regular_object
    assert GrahamStepsTablePydanticAdapter.from_regular_object(regular_object) == table_adapter


def test_steps_table_adapter_serialization(table_adapter):
    serialized_table = table_adapter.model_dump()
    deserialized_table = GrahamStepsTablePydanticAdapter(**serialized_table)
    assert deserialized_table.regular_object() == table_adapter.regular_object()