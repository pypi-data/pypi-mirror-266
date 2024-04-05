# -*- coding: utf-8 -*-
from typing import Union

import numpy as np
from numpy import ndarray

from sigmaepsilon.mesh.utils.topology.tr import Q8_to_T3, T6_to_T3
from sigmaepsilon.math.linalg.sparse.utils import count_cols


def RMatrix2x2toNumPy(RMatrix) -> ndarray:
    res = np.zeros((2, 2))
    res[0, 0] = RMatrix.e11
    res[0, 1] = RMatrix.e12
    res[1, 0] = RMatrix.e21
    res[1, 1] = RMatrix.e22
    return res


def RMatrix3x3toNumPy(RMatrix) -> ndarray:
    res = np.zeros((3, 3))
    res[0, 0] = RMatrix.e11
    res[0, 1] = RMatrix.e12
    res[0, 2] = RMatrix.e13
    res[1, 0] = RMatrix.e21
    res[1, 1] = RMatrix.e22
    res[1, 2] = RMatrix.e23
    res[2, 0] = RMatrix.e31
    res[2, 1] = RMatrix.e32
    res[2, 2] = RMatrix.e33
    return res


def RStiffness2dict(r) -> dict:
    return dict(x=r.x, y=r.y, z=r.z, xx=r.xx, yy=r.yy, zz=r.zz)


# %%


def xyz(r) -> list:
    return [r.x, r.y, r.z]


def sfcT6(r) -> list:
    return list(
        map(
            xyz,
            [
                r.pContourPoint1,
                r.pContourPoint2,
                r.pContourPoint3,
                r.pContourLineMidPoint1,
                r.pContourLineMidPoint2,
                r.pContourLineMidPoint3,
            ],
        )
    )


def sfcQ8(r) -> list:
    return list(
        map(
            xyz,
            [
                r.pContourPoint1,
                r.pContourPoint2,
                r.pContourPoint3,
                r.pContourPoint4,
                r.pContourLineMidPoint1,
                r.pContourLineMidPoint2,
                r.pContourLineMidPoint3,
                r.pContourLineMidPoint4,
            ],
        )
    )


def RSurfaceCoordinates2list(r) -> list:
    return sfcT6(r) if r.ContourPointCount == 3 else sfcQ8(r)


def RDisplacementValues2list(r) -> list:
    return [r.ex, r.ey, r.ez, r.Fx, r.Fy, r.Fz]


# %%


def getsfv(sfv) -> list:
    return [
        sfv.sfvNx,
        sfv.sfvNy,
        sfv.sfvNxy,
        sfv.sfvMx,
        sfv.sfvMy,
        sfv.sfvMxy,
        sfv.sfvVxz,
        sfv.sfvVyz,
    ]


def sfvT6(rec) -> list:
    return [
        getsfv(rec.sfvContourPoint1),
        getsfv(rec.sfvContourPoint2),
        getsfv(rec.sfvContourPoint3),
        getsfv(rec.sfvContourLineMidPoint1),
        getsfv(rec.sfvContourLineMidPoint2),
        getsfv(rec.sfvContourLineMidPoint3),
    ]


def sfvQ8(rec) -> list:
    return [
        getsfv(rec.sfvContourPoint1),
        getsfv(rec.sfvContourPoint2),
        getsfv(rec.sfvContourPoint3),
        getsfv(rec.sfvContourPoint4),
        getsfv(rec.sfvContourLineMidPoint1),
        getsfv(rec.sfvContourLineMidPoint2),
        getsfv(rec.sfvContourLineMidPoint3),
        getsfv(rec.sfvContourLineMidPoint4),
    ]


def RSurfaceForces2list(rec) -> list:
    return sfvT6(rec) if rec.ContourPointCount == 3 else sfvQ8(rec)


# %%


def get_stresses(rec) -> list:
    return [
        rec.ssvSxx,
        rec.ssvSyy,
        rec.ssvSxy,
        rec.ssvSxz,
        rec.ssvSyz,
        rec.ssvSVM,
        rec.ssvS1,
        rec.ssvS2,
        rec.ssvAs,
    ]


def get_ssv(rec, mode=None) -> list:
    if mode is None:
        return list(
            map(lambda r: get_stresses(r), [rec.ssvBottom, rec.ssvMiddle, rec.ssvTop])
        )
    if mode == "t":
        return get_stresses(rec.ssvTop)
    if mode == "m":
        return get_stresses(rec.ssvMiddle)
    if mode == "b":
        return get_stresses(rec.ssvBottom)


def ssvT6(rec, mode=None) -> list:
    return [
        get_ssv(rec.ssvtmbContourPoint1, mode=mode),
        get_ssv(rec.ssvtmbContourPoint2, mode=mode),
        get_ssv(rec.ssvtmbContourPoint3, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint1, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint2, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint3, mode=mode),
    ]


def ssvQ8(rec, mode=None) -> list:
    return [
        get_ssv(rec.ssvtmbContourPoint1, mode=mode),
        get_ssv(rec.ssvtmbContourPoint2, mode=mode),
        get_ssv(rec.ssvtmbContourPoint3, mode=mode),
        get_ssv(rec.ssvtmbContourPoint4, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint1, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint2, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint3, mode=mode),
        get_ssv(rec.ssvtmbContourLineMidPoint4, mode=mode),
    ]


def RSurfaceStresses2list(rec, mode=None) -> list:
    return (
        ssvT6(rec, mode=mode) if rec.ContourPointCount == 3 else ssvQ8(rec, mode=mode)
    )


# %%


def _get_lfv(lfv) -> list:
    return [
        lfv.lfvNx,
        lfv.lfvVy,
        lfv.lfvVz,
        lfv.lfvTx,
        lfv.lfvMy,
        lfv.lfvMz,
        lfv.lfvMyD,
    ]


def RLineForceValues2list(rec) -> list:
    return _get_lfv(rec)


# %%


def get_xssv(rec) -> list:
    return [
        rec.xssvSxx_m_T,
        rec.xssvSyy_m_T,
        rec.xssvSxy_m_T,
        rec.xssvSxx_m_B,
        rec.xssvSyy_m_B,
        rec.xssvSxy_m_B,
        rec.xssvSxx_n,
        rec.xssvSyy_n,
        rec.xssvSxy_n,
        rec.xssvSxz_max,
        rec.xssvSyz_max,
        rec.xssvSrx_max,
        rec.xssvSry_max,
    ]


def xssvT6(rec) -> list:
    return [
        get_xssv(rec.xssvContourPoint1),
        get_xssv(rec.xssvContourPoint2),
        get_xssv(rec.xssvContourPoint3),
        get_xssv(rec.xssvContourLineMidPoint1),
        get_xssv(rec.xssvContourLineMidPoint2),
        get_xssv(rec.xssvContourLineMidPoint3),
    ]


def xssvQ8(rec) -> list:
    return [
        get_xssv(rec.xssvContourPoint1),
        get_xssv(rec.xssvContourPoint2),
        get_xssv(rec.xssvContourPoint3),
        get_xssv(rec.xssvContourPoint4),
        get_xssv(rec.xssvContourLineMidPoint1),
        get_xssv(rec.xssvContourLineMidPoint2),
        get_xssv(rec.xssvContourLineMidPoint3),
        get_xssv(rec.xssvContourLineMidPoint4),
    ]


def RXLAMSurfaceStresses2list(rec) -> list:
    return xssvT6(rec) if rec.ContourPointCount == 3 else xssvQ8(rec)


def get_xlam_strs_case(resobj, cid, step, atype, i):
    return resobj.GetXLAMSurfaceStressesByLoadCaseId(i, cid, step, atype)[0]


def get_xlam_strs_comb(resobj, cid, step, atype, i):
    return resobj.GetXLAMSurfaceStressesByLoadCombinationId(i, cid, step, atype)[0]


def get_xsev(rec) -> list:
    return [rec.xsev_M_N_0, rec.xsev_M_N_90, rec.xsev_V_T, rec.xsev_Vr_N, rec.xsev_Max]


def xsevT6(rec) -> list:
    return [
        get_xsev(rec.xsevContourPoint1),
        get_xsev(rec.xsevContourPoint2),
        get_xsev(rec.xsevContourPoint3),
        get_xsev(rec.xsevContourLineMidPoint1),
        get_xsev(rec.xsevContourLineMidPoint2),
        get_xsev(rec.xsevContourLineMidPoint3),
    ]


def xsevQ8(rec) -> list:
    return [
        get_xsev(rec.xsevContourPoint1),
        get_xsev(rec.xsevContourPoint2),
        get_xsev(rec.xsevContourPoint3),
        get_xsev(rec.xsevContourPoint4),
        get_xsev(rec.xsevContourLineMidPoint1),
        get_xsev(rec.xsevContourLineMidPoint2),
        get_xsev(rec.xsevContourLineMidPoint3),
        get_xsev(rec.xsevContourLineMidPoint4),
    ]


def RXLAMSurfaceEfficiencies2list(rec) -> list:
    return xsevT6(rec) if rec.ContourPointCount == 3 else xsevQ8(rec)


def get_xlam_effs_crit(resobj, **params) -> list:
    return resobj.GetCriticalXLAMSurfaceEfficiencies(**params)[0]


# %%


def triangulate(topo, data=None):
    if isinstance(topo, ndarray):
        _, nNE = topo.shape
        if nNE == 6:
            if data is None:
                _, T3 = T6_to_T3(None, topo)
                return T3
            else:
                _, T3, data = T6_to_T3(None, topo, data=data)
                return T3, data
        elif nNE == 8:
            if data is None:
                _, T3 = Q8_to_T3(None, topo)
                return T3
            else:
                _, T3, data = Q8_to_T3(None, topo, data=data)
                return T3, data
        else:
            raise NotImplementedError
    else:
        w = count_cols(topo)
        i6 = np.where(w == 6)[0]
        i8 = np.where(w == 8)[0]
        if data is not None:
            assert len(data) == len(topo)
        try:
            if data is None:
                _, T3a = Q8_to_T3(None, topo[i8].to_numpy())
            else:
                _, T3a, data_a = Q8_to_T3(
                    None, topo[i8].to_numpy(), data=data[i8].to_numpy()
                )
        except Exception:
            if data is None:
                _, T3a = Q8_to_T3(None, topo[i8])
            else:
                _, T3a, data_a = Q8_to_T3(None, topo[i8], data=data[i8])
        try:
            if data is None:
                _, T3b = T6_to_T3(None, topo[i6].to_numpy())
            else:
                _, T3b, data_b = T6_to_T3(
                    None, topo[i6].to_numpy(), data=data[i6].to_numpy()
                )
        except Exception:
            if data is None:
                _, T3b = T6_to_T3(None, topo[i6])
            else:
                _, T3b, data_b = T6_to_T3(None, topo[i6], data=data[i6])
        if data is None:
            return np.vstack([T3a, T3b])
        else:
            return np.vstack([T3a, T3b]), np.vstack([data_a, data_b])


def dcomp2int(dcomp: str) -> int:
    assert isinstance(dcomp, str)
    dc = dcomp.lower()
    if dc in ["ex", "ux"]:
        return 0
    if dc in ["ey", "uy"]:
        return 1
    if dc in ["ez", "uz"]:
        return 2
    if dc in ["fx", "rotx"]:
        return 3
    if dc in ["fy", "roty"]:
        return 4
    if dc in ["fz", "rotz"]:
        return 5
    raise ValueError("Invalid displacement component '{}'".format(dcomp))


def fcomp2int(fcomp: str) -> int:
    assert isinstance(fcomp, str)
    fc = fcomp.lower()
    if fc == "nx":
        return 0
    if fc in "ny":
        return 1
    if fc in "nxy":
        return 2
    if fc == "mx":
        return 3
    if fc in "my":
        return 4
    if fc in "mxy":
        return 5
    if fc in ["vx", "vxz"]:
        return 6
    if fc in ["vy", "vyz"]:
        return 7
    raise ValueError("Invalid displacement component '{}'".format(fcomp))


def scomp2int(scomp: str) -> int:
    assert isinstance(scomp, str)
    sc = scomp.lower()
    if sc == "sxx":
        return 0
    if sc in "syy":
        return 1
    if sc in "sxy":
        return 2
    if sc == "sxz":
        return 3
    if sc in "syz":
        return 4
    if sc in "svm":
        return 5
    if sc in "s1":
        return 6
    if sc in "s2":
        return 7
    if sc in "as":
        return 8
    raise ValueError("Invalid stress component '{}'".format(scomp))


mtype2str = {
    0: "Other",
    1: "Steel",
    2: "Concrete",
    3: "Timber",
    4: "Aluminium",
    5: "Brick",
}


xlmstrcomp2int = dict(
    sxx_m_t=0,
    syy_m_t=1,
    sxy_m_t=2,
    sxx_m_b=3,
    syy_m_b=4,
    sxy_m_b=5,
    sxx_n=6,
    syy_n=7,
    sxy_n=8,
    sxz_max=9,
    syz_max=10,
    srx_max=11,
    sry_max=12,
)


def xlmscomp2int(scomp: str) -> int:
    assert isinstance(scomp, str)
    sc = scomp.lower()
    return xlmstrcomp2int[sc]


def _LoadLevelOrModeShapeOrTimeStep(
    load_level: int = None,
    mode_shape: int = None,
    time_step: int = None,
    return_none: bool = False,
    default: int = None,
) -> int:
    params = [load_level, mode_shape, time_step]
    is_param = list(map(lambda x: x is not None, params))
    num_params = sum(is_param)

    if num_params == 0:
        if return_none:
            assert (
                not default
            ), "If a default value is provided, 'return_none' should be False"
            return None
        elif default:
            return default

    if not sum(is_param) == 1:
        raise ValueError(
            "Exactly one of 'load_level', 'mode_sape' and 'time_step' must be provided"
        )

    return params[np.where(np.array(is_param))[0][0]]


def _DisplacementSystem(displacement_system: Union[str, int]) -> int:
    if displacement_system is None:
        return 1  # global

    if isinstance(displacement_system, str):
        if displacement_system == "local":
            return 0
        elif displacement_system == "global":
            return 1
        else:
            raise ValueError("Invalid specification for the displacement system")
    elif isinstance(displacement_system, int):
        return displacement_system

    raise Exception("Invalid specification for the displacement system")
