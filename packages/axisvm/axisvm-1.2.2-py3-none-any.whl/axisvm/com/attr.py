# -*- coding: utf-8 -*-
import awkward as ak
import pandas as pd


class AxisVMAttributes(dict):
    """
    A class to handle attributes.

    """

    def to_pandas(self, nested: bool = False) -> pd.DataFrame:
        """
        Returns the attributes as a Pandas DataFrame.
        """
        return pd.DataFrame.from_dict(self)

    def to_awkward(self, nested: bool = False) -> ak.Record:
        """
        Returns the attributes as an awkward Record.
        """
        return ak.Record(self)


def squeeze_attributes(d):
    return AxisVMAttributes({i: v[0] for i, v in d.items()})
