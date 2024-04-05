# -*- coding: utf-8 -*-
from typing import Iterable, Union, Any, Tuple
from functools import partial

import numpy as np
import awkward as ak
from numpy import ndarray

from sigmaepsilon.core import issequence
from sigmaepsilon.mesh import TopologyArray
from sigmaepsilon.mesh.utils.topology import unique_topo_data
from sigmaepsilon.mesh.utils.topology.tr import edges_Q4
from sigmaepsilon.mesh.utils.tri import edges_tri
from sigmaepsilon.mesh.utils.topology import detach as detach_mesh
from sigmaepsilon.mesh.plotting import triplot_plotly

import axisvm
from .core.wrap import AxisVMModelItem, AxisVMModelItems
from .core.utils import (
    RMatrix3x3toNumPy,
    triangulate,
    RSurfaceForces2list,
    RSurfaceStresses2list,
    get_xsev,
    RXLAMSurfaceStresses2list,
    get_xlam_strs_case,
    get_xlam_strs_comb,
    _LoadLevelOrModeShapeOrTimeStep,
    _DisplacementSystem,
)
from .attr import AxisVMAttributes
from .axresult import IAxisVMStresses

surfacetype_to_str = {
    0: "Hole",
    1: "MembraneStress",
    2: "MembraneStrain",
    3: "Plate",
    4: "Shell",
}

surface_attr_fields = [
    "Thickness",
    "SurfaceType",
    "RefZId",
    "RefXId",
    "MaterialId",
    "Characteristics",
    "ElasticFoundation",
    "NonLinearity",
    "Resistance",
]

surface_data_fields = [
    "N",
    "Attr",
    "DomainIndex",
    "LineIndex1",
    "LineIndex2",
    "LineIndex3",
    "LineIndex4",
]


def xyz(p):
    return [p.x, p.y, p.z]


def get_surface_attributes(
    obj, *args, i=None, fields=None, raw=False, rec=None, attr=None, **kwargs
):
    if fields is None:
        fields = surface_attr_fields
    elif isinstance(fields, str):
        fields = [fields]
    elif isinstance(fields, Iterable):
        fields = list(filter(lambda i: i in surface_attr_fields, fields))
    if attr is None:
        if rec is None:
            i = i if len(args) == 0 else args[0]
            rec = obj._get_attributes_raw(i)
        if raw:
            return rec
        else:
            rec = rec[0]
        attr = list(map(lambda r: r.Attr, rec))

    data = {}
    if "Thickness" in fields:
        data["Thickness"] = list(map(lambda a: a.Thickness, attr))
    if "SurfaceType" in fields:
        data["SurfaceType"] = list(
            map(lambda a: surfacetype_to_str[a.SurfaceType], attr)
        )
    if "RefXId" in fields:
        data["RefXId"] = list(map(lambda a: a.RefXId, attr))
    if "RefZId" in fields:
        data["RefZId"] = list(map(lambda a: a.RefZId, attr))
    if "MaterialId" in fields:
        data["MaterialId"] = list(map(lambda a: a.MaterialId, attr))
    if "Characteristics" in fields:
        data["Characteristics"] = list(map(lambda a: a.Charactersitics, attr))
    if "ElasticFoundation" in fields:
        data["ElasticFoundation"] = list(map(lambda a: xyz(a.ElasticFoundation), attr))
    if "NonLinearity" in fields:
        data["NonLinearity"] = list(map(lambda a: xyz(a.NonLinearity), attr))
    if "Resistance" in fields:
        data["Resistance"] = list(map(lambda a: xyz(a.Resistance), attr))
    return AxisVMAttributes(data)


class SurfaceMixin:
    def surface_edges(self, topology: ndarray = None) -> ndarray:
        """Returns the edges of the surface."""
        topo = self.topology() if topology is None else topology
        w = topo.widths()
        i6 = np.where(w == 6)[0]
        i8 = np.where(w == 8)[0]
        try:
            eT, _ = unique_topo_data(edges_tri(topo[i6, :3].to_numpy()))
        except Exception:
            eT, _ = unique_topo_data(edges_tri(topo[i6, :3]))
        try:
            eQ, _ = unique_topo_data(edges_Q4(topo[i8, :4].to_numpy()))
        except Exception:
            eQ, _ = unique_topo_data(edges_Q4(topo[i8, :4]))
        return np.vstack([eT, eQ])

    def triangles(self, topology: ndarray = None) -> ndarray:
        """Returns the topology as a collection of triangles."""
        topo = self.topology() if topology is None else topology
        return triangulate(topo)

    def plot(
        self,
        *,
        scalars=None,
        plot_edges=True,
        detach=False,
        backend="mpl",
        **__,
    ):
        """Plots the mesh using `matplotlib`."""
        topo = self.topology()
        triangles = self.triangles(topo) - 1
        edges = None
        if plot_edges:
            edges = self.surface_edges(topo) - 1
        if detach:
            # ids = np.unique(triangles) + 1
            coords = self.model.coordinates()
            coords, triangles = detach_mesh(coords, triangles)
        else:
            coords = self.model.coordinates()
        if backend == "mpl":
            pass
        return triplot_plotly(
            coords, triangles, data=scalars, plot_edges=plot_edges, edges=edges
        )


class IAxisVMSurface(AxisVMModelItem, SurfaceMixin):
    """Wrapper for the `IAxisVMSurface` COM interface."""

    def topology(self) -> TopologyArray:
        """Returns the node indices of the surface."""
        return self.parent.topology(self.Index)

    def record(self) -> Any:
        """Returns the record of the surface."""
        return self.parent.records(self.Index)

    def normal(self) -> ndarray:
        """Returns the normal vector of the surface."""
        return self.parent.normals(self.Index)

    def transformation_matrix(self) -> ndarray:
        """Returns the transformation matrix of the surface."""
        return self.parent.transformation_matrices(self.Index)

    @property
    def tr(self) -> ndarray:
        """Returns the transformation matrix of the surface."""
        return self.transformation_matrix()

    @property
    def attributes(self) -> dict:
        """Returns the attributes of the surface as a dictionary."""
        return self.parent.get_attributes(self.Index)

    @property
    def surface_attributes(self) -> dict:
        """Returns the surface attributes of the surface as a dictionary."""
        return self.parent.get_surface_attributes(self.Index)

    def xlam_stresses(
        self,
        case: Union[str, Iterable] = None,
        combination: Union[str, Iterable] = None,
        load_case_id: int = None,
        load_combination_id: int = None,
        displacement_system: int = 0,
        load_level: int = None,
        mode_shape: int = None,
        time_step: int = None,
        analysis_type: int = 0,
        frmt: str = "array",
        factor: Iterable = None,
    ) -> Union[dict, np.ndarray]:
        """
        Returns XLAM stresses either as a :class:`numpy.ndarray` or as a dictionary.

        Parameters
        ----------
        displacement_system: int, Optional
            0 for local, 1 for global. Default is 1.
        load_case_id: int, Optional
            Default is None.
        load_level: int, Optional
            Default is None.
        mode_shape: int, Optional
            Default is None.
        time_step: int, Optional
            Default is None.
        load_combination_id: int, Optional
            Default is None.
        case: Union[str, Iterable], Optional
            The name of a loadcase or an iterable of indices.
            Default is None.
        combination: str, Optional
            The name of a load combination. Default is None.
        analysis_type: int, Optional
            Default is 0.
        frmt: str, Optional
            Controls the type of the result. With 'array' it is a
            3d NumPy array, otherwise a dictionary. Default is 'array'.
        factor: Iterable, Optional
            Linear coefficients for the different load cases specified with 'case'.
            If 'case' is an Iterable, 'factor' must be an Iterable of the same shape.
            Default is None.

        Notes
        -----
        1) It is the user who has to make sure that this call is only called on surfaces,
        that belong to an XLAM domain.
        2) The returned stresses do not belong to the same position.

        Returns
        -------
        numpy.ndarray or dict
            If frmt is 'array', the result is a 2d float NumPy array of shape (nN, nX),
            where nN is the number of nodes of the surface and nX is the number of stress
            components, which are:

                * 0 : :math:`\\sigma_{x}` stress at the top, from bending
                * 1 : :math:`\\sigma_{y}` stress at the top, from bending
                * 2 : :math:`\\tau_{xy}` stress at the top, from bending
                * 3 : :math:`\\sigma_{x}` stress at the bottom, from bending
                * 4 : :math:`\\sigma_{y}` stress at the bottom, from bending
                * 5 : :math:`\\tau_{xy}` stress at the bottom, from bending
                * 6 : :math:`\\sigma_{x, max}` stress from stretching
                * 7 : :math:`\\sigma_{y, max}` stress from stretching
                * 8 : :math:`\\tau_{xy, max}` stress from stretching
                * 9 : :math:`\\tau_{xz, max}` shear stress
                * 10 : :math:`\\tau_{yz, max}` shear stress
                * 11 : :math:`\\tau_{xz, r, max}` rolling shear stress
                * 12 : :math:`\\tau_{yz, r, max}` rolling shear stress

            If frmt is 'dict', the stresses are returned as a dictionary of 1d NumPy arrays,
            where indices from 0 to 12 are the keys of the values at the corders.
        """
        # assert self.IsXLAM, "This is not an XLAM domain!"

        def ad2d(arr):
            return {i: arr[:, i] for i in range(13)}

        if issequence(case):
            if factor is not None:
                assert issequence(
                    factor
                ), "If 'case' is an Iterable, 'factor' must be an Iterable of the same shape."
                assert len(case) == len(
                    factor
                ), "Lists 'case' and 'factor' must have equal lengths."
                res = sum(
                    [
                        self.xlam_stresses(
                            case=c,
                            frmt="array",
                            factor=f,
                            analysis_type=analysis_type,
                            load_level=load_level,
                            mode_shape=mode_shape,
                            time_step=time_step,
                            displacement_system=displacement_system,
                        )
                        for c, f in zip(case, factor)
                    ]
                )
            else:
                res = [
                    self.xlam_stresses(
                        case=c,
                        frmt=frmt,
                        factor=1.0,
                        analysis_type=analysis_type,
                        load_level=load_level,
                        mode_shape=mode_shape,
                        time_step=time_step,
                        displacement_system=displacement_system,
                    )
                    for c in case
                ]
            if frmt == "dict":
                return ad2d(res)
            return res

        axm = self.model
        stresses: IAxisVMStresses = axm.Results.Stresses

        load_case_id, load_combination_id = stresses._get_case_or_component(
            case=case,
            combination=combination,
            load_case_id=load_case_id,
            load_combination_id=load_combination_id,
        )

        config = dict(
            load_case_id=load_case_id,
            load_combination_id=load_combination_id,
            load_level=load_level,
            mode_shape=mode_shape,
            time_step=time_step,
            displacement_system=displacement_system,
        )
        stresses.config(**config)

        LoadLevelOrModeShapeOrTimeStep = _LoadLevelOrModeShapeOrTimeStep(
            load_level=load_level,
            mode_shape=mode_shape,
            time_step=time_step,
            return_none=True,
        )
        if LoadLevelOrModeShapeOrTimeStep is None:
            LoadLevelOrModeShapeOrTimeStep = 1

        if load_case_id is not None:
            getter = partial(
                get_xlam_strs_case,
                stresses,
                load_case_id,
                LoadLevelOrModeShapeOrTimeStep,
                analysis_type,
            )
        elif load_combination_id is not None:
            getter = partial(
                get_xlam_strs_comb,
                stresses,
                load_combination_id,
                LoadLevelOrModeShapeOrTimeStep,
                analysis_type,
            )
        factor = 1.0 if factor is None else float(factor)
        res = factor * np.array(RXLAMSurfaceStresses2list(getter(self.Index)))

        if frmt == "dict":
            return ad2d(res)
        return res

    def critical_xlam_efficiency(
        self,
        *,
        combination_type: int = 7,
        analysis_type: int = 0,
        component: int = 4,
        minmax_type: int = 1,
        **kwargs,
    ) -> Tuple[Iterable]:
        """
        Returns the critical efficiency of a component, and also data on
        the combination that yields it.

        Parameters
        ----------
        minmax_type: int, Optional
            According to EMinMaxType. 0 for min, 1 for max, 2 for minmax. Default is 1.
        component: int, Optional
            According to EXLAMSurfaceEfficiency. Default is 4, which refers to the maximum overall efficiency.
        combination_type: int, Optional
            According to ECombinationType. Default is 7 wich refers to the worst case of ULS combinations.
        analysis_type: int, Optional
            According to EAnalysisType. Default is 0 which refers to linear statics.

        Notes
        -----
        It is the user who has to make sure that this call is only called on surfaces,
        that belong to an XLAM domain.

        Returns
        -------
        numpy.ndarray
            A 2d float NumPy array of shape (nN, nX), where nN is the number of nodes
            of the surface and nX is the number of efficiency components, which are:

                * 0 : M - N - 0
                * 1 : M - N - 90
                * 2 : V - T
                * 3 : Vr - N
                * 4 : max
        """
        axm = self.model
        stresses: IAxisVMStresses = axm.Results.Stresses
        params = dict(
            SurfaceId=self.Index,
            MinMaxType=minmax_type,
            CombinationType=combination_type,
            AnalysisType=analysis_type,
            Component=component,
        )
        params.update(kwargs)
        rec, _, factors, loadcases, _ = stresses.GetCriticalXLAMSurfaceEfficiency(
            **params
        )
        data = np.array(get_xsev(rec))
        return data, factors, loadcases

    def _get_attrs(self) -> Iterable:
        """Return the representation methods (internal helper)."""
        attrs = []
        attrs.append(("Index", self.Index, "{}"))
        attrs.append(("UID", self._wrapped.UID, "{}"))
        attrs.append(("Area", self.Area, axisvm.FLOAT_FORMAT))
        attrs.append(("Volume", self.Volume, axisvm.FLOAT_FORMAT))
        attrs.append(("Weight", self.Weight, axisvm.FLOAT_FORMAT))
        return attrs


class IAxisVMSurfaces(AxisVMModelItems, SurfaceMixin):
    """Wrapper for the `IAxisVMSurfaces` COM interface."""

    __itemcls__ = IAxisVMSurface

    @property
    def tr(self) -> ndarray:
        """Returns the transformation matrices for all surfaces."""
        return self.transformation_matrices()

    @property
    def t(self) -> ndarray:
        """Returns the thicknessws of all surfaces."""
        k = "Thickness"
        return np.array(self.get_surface_attributes(fields=[k])[k])

    @property
    def n(self) -> ndarray:
        """Returns the normal vectors of all surfaces."""
        return self.normals()

    @property
    def frames(self) -> ndarray:
        """Returns the transformation matrices for all surfaces."""
        return self.transformation_matrices()

    @property
    def attributes(self) -> dict:
        """Returns the attributes of all surfaces as a dictionary."""
        return self.get_attributes()

    @property
    def surface_attributes(self) -> AxisVMAttributes:
        """Returns the surface attributes of all surfaces as a dictionary."""
        return self.get_surface_attributes()

    def topology(self, *args, i: Union[int, Iterable[int]] = None) -> TopologyArray:
        """
        Returns the topology of the surfaces as an instance of :class:`sigmaepsilon.mesh.TopologyArray`.
        """
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            s = self[i]._wrapped
            data = list(s.GetContourPoints()[0]) + list(s.GetMidPoints()[0])
            return np.array(data, dtype=int)
        ids = None
        if isinstance(i, np.ndarray):
            ids = i
        else:
            if isinstance(i, Iterable):
                ids = np.array(i, dtype=int)
            else:
                ids = np.array(list(range(self.Count))) + 1
        if ids is not None:
            s = self._wrapped

            def fnc_corner(i):
                return list(s[i].GetContourPoints()[0])

            def fnc_mid(i):
                return list(s[i].GetMidPoints()[0])

            def fnc(i):
                return fnc_corner(i) + fnc_mid(i)

            return TopologyArray(ak.Array(list(map(fnc, ids))))
        return None

    def records(self, *args, **kwargs) -> Iterable[dict]:
        """
        Returns the raw attributes of the surfaces.
        """
        return self._get_attributes_raw(*args, **kwargs)[0]

    def get_attributes(
        self,
        *args,
        i: Union[int, Iterable[int]] = None,
        fields: Iterable[str] = None,
        raw: bool = False,
        **__,
    ) -> Iterable[dict]:
        """
        Returns the attributes of the surfaces.
        """
        i = i if len(args) == 0 else args[0]
        dfields, afields = [], []
        if fields is None:
            afields = surface_attr_fields
            dfields = surface_data_fields
        else:
            if isinstance(fields, str):
                fields = [fields]
            if isinstance(fields, Iterable):
                afields = list(filter(lambda i: i in surface_attr_fields, fields))
                dfields = list(filter(lambda i: i in surface_data_fields, fields))
        fields = dfields + afields
        rec_raw = self._get_attributes_raw(i)
        if raw:
            return rec_raw
        else:
            rec = rec_raw[0]
        data = {}
        if "Attr" in fields:
            data.update(self.get_surface_attributes(_rec=rec_raw))
        else:
            if len(afields) > 0:
                attr = self.get_surface_attributes(_rec=rec_raw, fields=afields)
                for f in afields:
                    data[f] = attr[f]
        if "N" in dfields:
            data["N"] = list(map(lambda r: r.N, rec))
        if "DomainIndex" in dfields:
            data["DomainIndex"] = list(map(lambda r: r.DomainIndex, rec))
        if "LineIndex1" in dfields:
            data["LineIndex1"] = list(map(lambda r: r.LineIndex1, rec))
        if "LineIndex2" in dfields:
            data["LineIndex2"] = list(map(lambda r: r.LineIndex2, rec))
        if "LineIndex3" in dfields:
            data["LineIndex3"] = list(map(lambda r: r.LineIndex3, rec))
        if "LineIndex4" in dfields:
            data["LineIndex4"] = list(map(lambda r: r.LineIndex4, rec))
        return AxisVMAttributes(data)

    def _get_attributes_raw(self, *args, i=None) -> Iterable:
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
        return self.model.Surfaces.BulkGetSurfaces(ids)

    def get_surface_attributes(self, *args, **kwargs) -> AxisVMAttributes:
        """Returns the surface attributes of all surfaces as a dictionary."""
        return get_surface_attributes(self, *args, **kwargs)

    def normals(self, *args, i=None) -> ndarray:
        """
        Returns the normal vectors of the surfaces as a NumPy array.
        """
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            s = self[i]._wrapped

            def xyz(p):
                return [p.x, p.y, p.z]

            return np.array(xyz(s.GetNormalVector()[0]), dtype=float)
        if isinstance(i, np.ndarray):
            inds = i
        else:
            if isinstance(i, Iterable):
                inds = np.array(i, dtype=int)
            else:
                inds = np.array(list(range(self.Count))) + 1
        s = self._wrapped
        m = map(lambda i: s.Item[i].GetNormalVector()[0], inds)
        xyz = map(lambda p: [p.x, p.y, p.z], m)
        return np.array(list(xyz), dtype=float)

    def transformation_matrices(
        self, *args, i: Union[int, Iterable[int]] = None
    ) -> ndarray:
        """
        Returns the transformation matrices of the surfaces as a NumPy array.
        """
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            s = self[i]._wrapped
            return np.array(RMatrix3x3toNumPy(s.GetTrMatrix()[0]), dtype=float)
        if isinstance(i, np.ndarray):
            inds = i
        else:
            if isinstance(i, Iterable):
                inds = np.array(i, dtype=int)
            else:
                inds = np.array(list(range(self.Count))) + 1
        s = self._wrapped
        rec = list(map(lambda i: s.Item[i].GetTrMatrix()[0], inds))
        return np.array(list(map(RMatrix3x3toNumPy, rec)), dtype=float)

    def generalized_surface_forces(
        self,
        *,
        case: str = None,
        combination: str = None,
        displacement_system: int = None,
        load_case_id: int = None,
        load_combination_id: int = None,
        load_level: int = None,
        mode_shape: int = None,
        time_step: int = None,
        **__,
    ) -> ak.Array:
        axm = self.model
        if case is not None:
            load_combination_id = None
            if isinstance(case, str):
                LoadCases = axm.LoadCases
                imap = {LoadCases.Name[i]: i for i in range(1, LoadCases.Count + 1)}
                if case in imap:
                    load_case_id = imap[case]
                else:
                    raise KeyError("Unknown case with name '{}'".format(case))
            elif isinstance(case, int):
                load_case_id = case
        elif combination is not None:
            load_case_id = None
            if isinstance(combination, str):
                LoadCombinations = axm.LoadCombinations
                imap = {
                    LoadCombinations.Name[i]: i
                    for i in range(1, LoadCombinations.Count + 1)
                }
                if combination in imap:
                    load_combination_id = imap[combination]
                else:
                    raise KeyError(
                        "Unknown combination with name '{}'".format(combination)
                    )
            elif isinstance(combination, int):
                load_combination_id = combination

        forces = axm.Results.Forces

        forces.DisplacementSystem = _DisplacementSystem(displacement_system)

        if load_case_id is not None:
            forces.LoadCaseId = load_case_id

        if load_combination_id is not None:
            forces.LoadCombinationId = load_combination_id

        forces.LoadLevelOrModeShapeOrTimeStep = _LoadLevelOrModeShapeOrTimeStep(
            load_level=load_level, mode_shape=mode_shape, time_step=time_step, default=1
        )

        if load_case_id is not None:
            recs = forces.AllSurfaceForcesByLoadCaseId()[0]

        elif load_combination_id is not None:
            recs = forces.AllSurfaceForcesByLoadCombinationId()[0]

        return ak.Array(list(map(RSurfaceForces2list, recs)))

    def surface_stresses(
        self,
        *,
        case: str = None,
        combination: str = None,
        displacement_system: Union[str, int] = None,
        load_case_id: int = None,
        load_level: int = None,
        mode_shape: int = None,
        time_step: int = None,
        load_combination_id: int = None,
        z: str = "m",
        **__,
    ) -> ak.Array:
        axm = self.model
        if case is not None:
            load_combination_id = None
            if isinstance(case, str):
                LoadCases = axm.LoadCases
                imap = {LoadCases.Name[i]: i for i in range(1, LoadCases.Count + 1)}
                if case in imap:
                    load_case_id = imap[case]
                else:
                    raise KeyError("Unknown case with name '{}'".format(case))
            elif isinstance(case, int):
                load_case_id = case
        elif combination is not None:
            load_case_id = None
            if isinstance(combination, str):
                LoadCombinations = axm.LoadCombinations
                imap = {
                    LoadCombinations.Name[i]: i
                    for i in range(1, LoadCombinations.Count + 1)
                }
                if combination in imap:
                    load_combination_id = imap[combination]
                else:
                    raise KeyError(
                        "Unknown combination with name '{}'".format(combination)
                    )
            elif isinstance(combination, int):
                load_combination_id = combination
            else:
                raise TypeError("'load_combination_id' must be a string or an integer.")

        resobj: IAxisVMStresses = axm.Results.Stresses

        resobj.DisplacementSystem = _DisplacementSystem(displacement_system)

        if load_case_id is not None:
            resobj.LoadCaseId = load_case_id

        if load_combination_id is not None:
            resobj.LoadCombinationId = load_combination_id

        resobj.LoadLevelOrModeShapeOrTimeStep = _LoadLevelOrModeShapeOrTimeStep(
            load_level=load_level, mode_shape=mode_shape, time_step=time_step, default=1
        )

        if load_case_id is not None:
            recs = resobj.AllSurfaceStressesByLoadCaseId()[0]

        elif load_combination_id is not None:
            recs = resobj.AllSurfaceStressesByLoadCombinationId()[0]

        foo = partial(RSurfaceStresses2list, mode=z)
        return ak.Array(list(map(foo, recs)))

    def _get_attrs(self) -> Iterable:
        """Return the representation methods (internal helper)."""
        attrs = []
        attrs.append(("Index", self.Index, "{}"))
        attrs.append(("UID", self._wrapped.UID, "{}"))
        attrs.append(("Area", self.Area, axisvm.FLOAT_FORMAT))
        attrs.append(("Volume", self.Volume, axisvm.FLOAT_FORMAT))
        attrs.append(("Weight", self.Weight, axisvm.FLOAT_FORMAT))
        return attrs
