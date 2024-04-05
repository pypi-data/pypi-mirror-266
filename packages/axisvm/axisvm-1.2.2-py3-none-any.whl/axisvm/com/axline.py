# -*- coding: utf-8 -*-
from typing import Iterable

import awkward as ak
import numpy as np
from numpy import ndarray as Array
from sigmaepsilon.mesh import TopologyArray
from sigmaepsilon.mesh.plotting import plot_lines_plotly

import axisvm

from .core.abc import AxisVMModelItem, AxisVMModelItems
from .core.utils import RMatrix3x3toNumPy, RStiffness2dict
from .attr import AxisVMAttributes


linetype_to_str = {
    0: "Truss",
    1: "Beam",
    2: "Rib",
    3: "Spring",
    4: "Gap",
    5: "Edge",
    6: "Hole",
    7: "SimpleLine",
    8: "NNLink",
    9: "LLLink",
}

springdir_to_str = {
    0: "Global",
    1: "Geometry",
    2: "PointReference",
    3: "VectorReference",
    4: "ElementRelative",
    5: "NodeRelative",
}

trusstype_to_str = {
    0: "TensionAndCompression",  # linear behaviour
    1: "TensionOnly",  # tension only
    2: "CompressionOnly",  # compression only
}

gaptype_to_str = {
    0: "ActiveInTension",  # gap active in tension only
    1: "ActiveInCompression",  # gap active in compression only
}

geomtype_to_str = {
    0: "StraightLine",
    1: "CircleArc",
}

line_data_fields = ["NodeId1", "NodeId2", "GeomType", "CircleArc"]

line_attr_fields = [
    "LineType",
    "MaterialIndex",
    "StartCrossSectionIndex",
    "EndCrossSectionIndex",
    "AutoEccentricityType",
]


def get_line_attributes(
    obj, *args, i=None, fields=None, raw=False, rec=None, **kwargs
) -> AxisVMAttributes:
    """
    Turns a collection of RLineAttr records into dictionaries compatible
    with `awkward` and `pandas`.

    """
    if fields is None:
        fields = line_attr_fields
    elif isinstance(fields, str):
        fields = [fields]
    elif isinstance(fields, Iterable):
        fields = list(filter(lambda i: i in line_attr_fields, fields))
    if rec is None:
        i = i if len(args) == 0 else args[0]
        rec = obj._get_attributes_raw(i)
    if raw:
        return rec
    else:
        rec = rec[0]

    def xyz(p):
        return [p.x, p.y, p.z]

    def xyz2(p):
        return [p.xx, p.yy, p.zz]

    data = {}

    if "LineType" in fields:
        data["LineType"] = list(map(lambda r: linetype_to_str[r.LineType], rec))
    if "MaterialIndex" in fields:
        data["MaterialIndex"] = list(map(lambda r: r.MaterialIndex, rec))
    if "StartCrossSectionIndex" in fields:
        data["StartCrossSectionIndex"] = list(
            map(lambda r: r.StartCrossSectionIndex, rec)
        )
    if "EndCrossSectionIndex" in fields:
        data["EndCrossSectionIndex"] = list(map(lambda r: r.EndCrossSectionIndex, rec))
    if "AutoEccentricityType" in fields:
        data["AutoEccentricityType"] = list(map(lambda r: r.AutoEccentricityType, rec))
    if "StartEccentricity" in fields:
        data["StartEccentricity"] = list(
            map(lambda r: RMatrix3x3toNumPy(r.StartEccentricity), rec)
        )
    if "EndEccentricity" in fields:
        data["EndEccentricity"] = list(
            map(lambda r: RMatrix3x3toNumPy(r.EndEccentricity), rec)
        )
    if "TrussType" in fields:
        data["TrussType"] = list(map(lambda r: trusstype_to_str[r.TrussType], rec))
    if "Resistance" in fields:
        data["Resistance"] = list(map(lambda r: r.Resistance, rec))

    if "ServiceClass" in fields:
        data["ServiceClass"] = list(map(lambda r: r.ServiceClass, rec))
    if "kdef" in fields:
        data["kdef"] = list(map(lambda r: r.kdef, rec))
    if "kx" in fields:
        data["kx"] = list(map(lambda r: r.kx, rec))
    if "Domain1" in fields:
        data["Domain1"] = list(map(lambda r: r.Domain1, rec))
    if "Domain2" in fields:
        data["Domain2"] = list(map(lambda r: r.Domain2, rec))

    if "GapType" in fields:
        data["GapType"] = list(map(lambda r: gaptype_to_str[r.GapType], rec))
    if "ActiveStiffness" in fields:
        data["ActiveStiffness"] = list(map(lambda r: r.ActiveStiffness, rec))
    if "InactiveStiffness" in fields:
        data["InactiveStiffness"] = list(map(lambda r: r.InactiveStiffness, rec))
    if "InitialOpening" in fields:
        data["InitialOpening"] = list(map(lambda r: r.InitialOpening, rec))
    if "MinPenetration" in fields:
        data["MinPenetration"] = list(map(lambda r: r.MinPenetration, rec))
    if "MaxPenetration" in fields:
        data["MaxPenetration"] = list(map(lambda r: r.MaxPenetration, rec))
    if "AdjustmentRatio" in fields:
        data["AdjustmentRatio"] = list(map(lambda r: r.AdjustmentRatio, rec))
    if "SpringDirection" in fields:
        data["SpringDirection"] = list(
            map(lambda r: springdir_to_str[r.SpringDirection], rec)
        )
    if "Stiffnesses" in fields:
        data["Stiffnesses"] = list(map(lambda r: RStiffness2dict(r.Stiffnesses), rec))

    return AxisVMAttributes(data)


class IAxisVMLine(AxisVMModelItem):
    """Wrapper for the `IAxisVMLine` COM interface."""

    @property
    def Index(self):
        return self.parent.IndexOf(self.StartNode, self.EndNode)

    @property
    def attributes(self):
        return self.parent.get_attributes(self.Index)

    @property
    def line_attributes(self):
        return self.parent.get_line_attributes(self.Index)

    @property
    def line_data(self):
        return self.parent.get_line_data(self.Index)

    @property
    def tr(self):
        return self.transformation_matrix()

    def record(self):
        return self.parent.records(self.Index)

    def _get_attrs(self):
        """Return the representation methods (internal helper)."""
        attrs = []
        attrs.append(("Length", self.Length, axisvm.FLOAT_FORMAT))
        attrs.append(("Volume", self.Volume, axisvm.FLOAT_FORMAT))
        attrs.append(("Weight", self.Weight, axisvm.FLOAT_FORMAT))
        return attrs

    def topology(self) -> TopologyArray:
        return TopologyArray(ak.Array([self.StartNode, self.EndNode]))

    def transformation_matrix(self) -> Array:
        return self.model.Members[self.MemberId].transformation_matrix()


class IAxisVMLines(AxisVMModelItems):
    """Wrapper for the `IAxisVMLines` COM interface."""

    __itemcls__ = IAxisVMLine

    @property
    def frames(self) -> Array:
        return self.transformation_matrices()

    @property
    def attributes(self):
        return self.get_attributes()

    @property
    def line_attributes(self):
        return self.get_line_attributes()

    @property
    def line_data(self):
        return self.get_line_data()

    @property
    def tr(self):
        return self.transformation_matrices()

    def records(self, *args, **kwargs):
        return self.get_line_data(*args, raw=True, **kwargs)

    def topology(self, *args, i=None) -> TopologyArray:
        lines = self.wrapped
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            line = self[i].wrapped
            return TopologyArray(ak.Array([line.StartNode, line.EndNode]))
        if isinstance(i, np.ndarray):
            inds = i
        else:
            if isinstance(i, Iterable):
                inds = np.array(i, dtype=int)
            else:
                inds = np.array(list(range(lines.Count))) + 1

        def fnc(i):
            return [lines.Item[i].StartNode, lines.Item[i].EndNode]

        return TopologyArray(ak.Array(list(map(fnc, inds))))

    def transformation_matrices(self, *args, i=None) -> Array:
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            ids = [i]
        if isinstance(i, np.ndarray):
            ids = i
        else:
            if isinstance(i, Iterable):
                ids = np.array(i, dtype=int)
            else:
                ids = np.array(list(range(self.Count))) + 1
        mids = np.array(self.BulkGetMemberIds(ids)[0])
        if len(mids) == 1:
            return self.model.Members[mids[0]].transformation_matrix()
        uids, imap = np.unique(mids, return_inverse=True)
        mtr = self.model.Members.transformation_matrices(uids)
        imap -= 1
        return np.array(list(map(lambda i: mtr[i], imap)))

    def _get_line_data_raw(self, *args, i=None) -> Iterable:
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            ids = np.array([i])
        elif isinstance(i, np.ndarray):
            ids = i
        else:
            if isinstance(i, Iterable):
                ids = np.array(i, dtype=int)
            else:
                ids = np.array(list(range(self.Count))) + 1
        return self.BulkGetLineData(ids)

    def get_line_data(self, *args, i=None, fields=None, raw=False) -> AxisVMAttributes:
        if fields is None:
            fields = line_data_fields
        elif isinstance(fields, str):
            fields = [fields]
        elif isinstance(fields, Iterable):
            fields = list(filter(lambda i: i in line_data_fields, fields))
        i = i if len(args) == 0 else args[0]
        rec = self._get_line_data_raw(i)
        if raw:
            return rec
        else:
            rec = rec[0]
        data = {}
        if "NodeId1" in fields:
            data["NodeId1"] = list(map(lambda r: r.NodeId1, rec))
        if "NodeId2" in fields:
            data["NodeId2"] = list(map(lambda r: r.NodeId2, rec))
        if "GeomType" in fields:
            data["GeomType"] = list(map(lambda r: geomtype_to_str[r.GeomType], rec))
        if "CircleArc" in fields:

            def xyz(p):
                return [p.x, p.y, p.z]

            def foo(ca):
                return dict(
                    Center=xyz(ca.Center),
                    NormalVector=xyz(ca.NormalVector),
                    Alfa=ca.Alfa,
                )

            def CircleArc(r):
                return foo(r.CircleArc) if r.GeomType == 1 else None

            data["CircleArc"] = list(map(CircleArc, rec))
        return AxisVMAttributes(data)

    def _get_line_attributes_raw(self, *args, i=None, **kwargs) -> Iterable:
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            ids = np.array([i])
        if isinstance(i, np.ndarray):
            ids = i
        else:
            if isinstance(i, Iterable):
                ids = np.array(i, dtype=int)
            else:
                ids = np.array(list(range(self.Count))) + 1
        return self.BulkGetAttr(ids)

    def _get_attributes_raw(self, *args, **kwargs) -> AxisVMAttributes:
        return self._get_line_attributes_raw(*args, **kwargs)

    def get_line_attributes(self, *args, **kwargs) -> AxisVMAttributes:
        return get_line_attributes(self, *args, **kwargs)

    def get_attributes(self, *args, fields=None, **kwargs) -> AxisVMAttributes:
        dfields, afields = [], []
        if fields is None:
            afields = line_attr_fields
            dfields = line_data_fields
        else:
            if isinstance(fields, str):
                fields = [fields]
            if isinstance(fields, Iterable):
                afields = list(filter(lambda i: i in line_attr_fields, fields))
                dfields = list(filter(lambda i: i in line_data_fields, fields))
        res = {}
        if len(afields) > 0:
            res.update(self.get_line_attributes(*args, fields=afields, **kwargs))
        if len(dfields) > 0:
            res.update(self.get_line_data(*args, fields=dfields, **kwargs))
        return AxisVMAttributes(res)

    def plot(self, *args, **kwargs):
        coords = self.model.coordinates()
        topo = self.topology().to_numpy() - 1
        return plot_lines_plotly(coords, topo, *args, **kwargs)
