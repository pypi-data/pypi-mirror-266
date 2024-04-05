from typing import Iterable

from testbook import testbook


def get_code_cells_of_testbook(tb: testbook) -> Iterable[int]:
    return [i for i, cell in enumerate(tb.cells) if cell.cell_type == "code"]


def inject_AxisVM_into_testbook(tb: testbook, after:int) -> None:
    code_to_injext = """
from axisvm.com.client import start_AxisVM
axisvm_application = start_AxisVM(visible=True, join=True, daemon=True)
"""     
    tb.inject(code_to_injext, after=after)