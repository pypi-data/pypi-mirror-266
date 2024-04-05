import pytest
from testbook import testbook

from axisvm.com.axapp import IAxisVMApplication
from .utils import get_code_cells_of_testbook, inject_AxisVM_into_testbook


def test_moving_loads_on_a_beam(axisvm_application: IAxisVMApplication):
    with testbook(
        "docs/source/notebooks/moving_loads_on_a_beam.ipynb", execute=False
    ) as tb:
        code_cell_indices = get_code_cells_of_testbook(tb)

        inject_AxisVM_into_testbook(tb, after=code_cell_indices[0])

        for index in code_cell_indices[1:-1]:
            tb.execute_cell(index)


def test_adding_cross_sections(axisvm_application: IAxisVMApplication):
    with testbook(
        "docs/source/notebooks/adding_cross_sections.ipynb", execute=False
    ) as tb:
        code_cell_indices = get_code_cells_of_testbook(tb)

        inject_AxisVM_into_testbook(tb, after=code_cell_indices[0])

        for index in code_cell_indices[1:-1]:
            tb.execute_cell(index)


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
