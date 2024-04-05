# -*- coding: utf-8 -*-
import os
import appdirs
import warnings
from typing import Optional
from importlib.metadata import metadata

__pkg_metadata__ = metadata("axisvm")
__version__ = __pkg_metadata__["version"]
__description__ = __pkg_metadata__["summary"]
del __pkg_metadata__

# catch annoying numpy/vtk future warning:
warnings.simplefilter(action="ignore", category=FutureWarning)

# If available, a local vtk-data instance will be used for examples
AXISVM_DATA_PATH: Optional[str] = None
if "AXISVM_DATA_PATH" in os.environ:
    AXISVM_DATA_PATH = os.environ["AXISVM_DATA_PATH"]
    if not os.path.isdir(AXISVM_DATA_PATH):
        warnings.warn(f"AXISVM_DATA_PATH: {AXISVM_DATA_PATH} is an invalid path")
    if not os.path.isdir(os.path.join(AXISVM_DATA_PATH, "Data")):
        warnings.warn(
            f"AXISVM_DATA_PATH: {os.path.join(AXISVM_DATA_PATH, 'Data')} does not exist"
        )

# allow user to override the examples path
if "AXISVM_USERDATA_PATH" in os.environ:
    USER_DATA_PATH = os.environ["AXISVM_USERDATA_PATH"]
    if not os.path.isdir(USER_DATA_PATH):
        raise FileNotFoundError(f"Invalid AXISVM_USERDATA_PATH at {USER_DATA_PATH}")
else:
    USER_DATA_PATH = appdirs.user_data_dir("AXISVM")
    try:
        # Set up data directory
        os.makedirs(USER_DATA_PATH, exist_ok=True)
    except Exception as e:
        warnings.warn(
            f'Unable to create `AXISVM_USERDATA_PATH` at "{USER_DATA_PATH}"\n'
            f"Error: {e}\n\n"
            "Override the default path by setting the environmental variable "
            "`AXISVM_USERDATA_PATH` to a writable path."
        )
        USER_DATA_PATH = ""

EXAMPLES_PATH = os.path.join(USER_DATA_PATH, "examples")
try:
    os.makedirs(EXAMPLES_PATH, exist_ok=True)
except Exception as e:
    warnings.warn(
        f'Unable to create `EXAMPLES_PATH` at "{EXAMPLES_PATH}"\n'
        f"Error: {e}\n\n"
        "Override the default path by setting the environmental variable "
        "`AXISVM_USERDATA_PATH` to a writable path."
    )
    EXAMPLES_PATH = ""


# Set a parameter to control default print format for floats outside
# of the plotter
FLOAT_FORMAT = "{:.3e}"
