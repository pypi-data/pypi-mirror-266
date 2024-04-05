# -*- coding: utf-8 -*-
from typing import List

from .core.wrap import AxWrapper

__all__ = ["IAxisVMLoadCombinations"]


combinationtype2name = {
    0: "Other",
    1: "SLS Characteristic",
    2: "SLS Frequent",
    3: "SLS Quasipermanent",
    4: "ULS Fundamental",
    5: "ULS Seismic",
    6: "ULS Exceptional",
    7: "ULS All",
    8: "ULS (a, b)",
    9: "ULS a",
    10: "ULS b",
    11: "ULS All (a, b)",
    12: "ULS A1",
    13: "ULS A2",
    14: "ULS A3",
    15: "ULS A4",
    16: "ULS A5",
    17: "ULS A6",
    18: "ULS A7",
    19: "ULS A8",
    20: "ULS All SE1",
    21: "ULS All SE2",
    22: "ULS All SE3",
    23: "ULS All SE4",
    24: "ULS All SE5",
    25: "ULS All SE6",
    26: "ULS All SE7",
    27: "ULS All SE8",
    28: "SLS Semi Auto SLS1",
    29: "SLS Semi Auto SLS2",
    30: "SLS Semi Auto SLS3",
    31: "Automatic",
}


combinationname2type = {v: k for k, v in combinationtype2name.items()}


class IAxisVMLoadCombinations(AxWrapper):
    """Wrapper for the `IAxisVMModel` COM interface."""

    def valid_load_combination_types(self) -> List[int]:
        """
        Returns valid load combination types.
        """
        result, retval = self._wrapped.GetValidCombinationTypes()
        if retval < 0:
            raise Exception(f"Error code: {retval}")
        else:
            return result

    def valid_load_combination_names(self) -> List[str]:
        """
        Returns the names of valid load combination types.
        """
        ids = self.valid_load_combination_types()
        return [combinationtype2name[i] for i in ids]

    def combination_name_to_type(self, name: str) -> int:
        """
        Returns the type (int) of the combination from its name
        according to :func:`valid_combination_names`.
        """
        return combinationname2type[name]

    def combination_type_to_name(self, combination_type: int) -> str:
        """
        Returns the name of the combination from its type (ECombinationType)
        according to :func:`valid_combination_names`.
        """
        return combinationtype2name[combination_type]
