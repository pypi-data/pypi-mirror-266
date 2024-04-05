import pytest, time

from axisvm.com.client import start_AxisVM
from axisvm.com.axapp import IAxisVMApplication


@pytest.fixture(scope="session")
def axisvm_application() -> IAxisVMApplication:
    """
    Setting up the AxisVM instance.
    """
    axisvm_application = start_AxisVM(visible=True, daemon=True)
    time.sleep(10)
    yield axisvm_application
    axisvm_application.Quit()
