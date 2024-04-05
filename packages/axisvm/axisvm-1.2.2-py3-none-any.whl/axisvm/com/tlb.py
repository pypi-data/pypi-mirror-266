# -*- coding: utf-8 -*-


def find_axisvm_tlb():
    """
    Finds all registered AxisVM Type Libraries and
    returns a list of dictionaries including all important
    specs. If the function returns more than one item,
    consider unregistering the ones you don't use.

    Example
    -------
    >>> from axisvm.com.tlb import find_axisvm_tlb
    >>> axtlb = find_axisvm_tlb()
    """
    from win32com.client.selecttlb import FindTlbsWithDescription

    items = FindTlbsWithDescription("AxisVM Library")
    # fixup versions - we expect hex
    for i in items:
        i.major = int(i.major, 16)
        i.minor = int(i.minor, 16)
    return list(map(lambda i: i.__dict__, items))


def wrap_axisvm_tlb(tlbid=None, major=None, minor=None):
    """
    Returns the wrapped AxisVM type library as a python module.
    The library to wrap can be specified by Id, minor and major
    version numbers, but all three must be provided to have a
    complete specification. Otherwise, the function returns a python
    module for the first AxisVM type library found by the function
    :func:`find_axisvm_tlb`.

    Parameters
    ----------
    tlbid : str, Optional
        Id of the type library to wrap.
        Defaut is None.

    major : int, Optional
        Major version number of the type library to wrap.
        Defaut is None.

    minor : int, Optional
        Minor version number of the type library to wrap.
        Defaut is None.

    Example
    -------
    >>> from axisvm.com.tlb import wrap_axisvm_tlb
    >>> axtlb = wrap_axisvm_tlb("{0AA46C32-04EF-46E3-B0E4-D2DA28D0AB08}", 15, 1)

    Note
    ----
    All three specifiers must be provided, otherwise the function
    inherits the specifications from

    Returns
    -------
    module
        The wrapped AxisVM type library as a python module.

    """
    from comtypes import client as cc

    if tlbid is None or major is None or minor is None:
        from comtypes import GUID as comGUID

        tlb = find_axisvm_tlb()[0]
        tlbid = comGUID(tlb["clsid"])
        major, minor = tlb["major"], tlb["minor"]
    return cc.GetModule((tlbid, major, minor))


try:
    from comtypes.gen import AxisVM

    globals().update(AxisVM.__dict__)
except Exception:
    tlb = wrap_axisvm_tlb()
    globals().update(tlb.__dict__)
