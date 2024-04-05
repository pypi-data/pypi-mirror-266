# -*- coding: utf-8 -*-
from .core.wrap import AxisVMModelItem, AxisVMModelItems
from .core.utils import mtype2str


class IAxisVMMaterial(AxisVMModelItem):
    """Wrapper for the `IAxisVMMaterial` COM interface."""

    def _get_attrs(self):
        """Return the representation methods (internal helper)."""
        attrs = []
        NDN = self.NationalDesignName
        attrs.append(("Name", self.Name, "{}"))
        attrs.append(("NationalDesignName", self.NationalDesignName, "{}"))
        attrs.append(("MaterialDesignName", self.MaterialDesignName, "{}"))
        attrs.append(("MaterialType", mtype2str[self.MaterialType], "{}"))
        attrs.append(("UID", self._wrapped.UID, "{}"))

        mtype = self.MaterialType
        if mtype == 1:
            # steel
            if NDN == "Eurcode":
                attrs.append(("Fu", self._wrapped.Fu, "{}"))
                attrs.append(("Fu40", self._wrapped.Fu40, "{}"))
                attrs.append(("Fy", self._wrapped.Fy, "{}"))
                attrs.append(("Fy40", self._wrapped.Fy40, "{}"))
        elif mtype == 3:
            # timber
            attrs.append(("TimberType", self._wrapped.TimberType, "{}"))
            attrs.append(("E005", self._wrapped.E005, "{}"))
            attrs.append(("GMean", self._wrapped.GMean, "{}"))
            attrs.append(("GammaM", self._wrapped.GammaM, "{}"))
            attrs.append(("fmk", self._wrapped.fmk, "{}"))
            attrs.append(("ft0k", self._wrapped.ft0k, "{}"))
            attrs.append(("fc90ky", self._wrapped.fc90ky, "{}"))
            attrs.append(("fc90kz", self._wrapped.fc90kz, "{}"))
            attrs.append(("fvkz", self._wrapped.fvkz, "{}"))
            attrs.append(("fvky", self._wrapped.fvky, "{}"))
        return attrs

    @property
    def linear_properties(self):
        return {
            "EX": self._wrapped.Ex,
            "EY": self._wrapped.Ey,
            "EZ": self._wrapped.Ez,
            "NUXY": self._wrapped.Nux,
            "NUXZ": self._wrapped.Nuy,
            "NUYZ": self._wrapped.Nuz,
            "AlphaX": self._wrapped.AlfaX,
            "AlphaY": self._wrapped.AlfaY,
            "AlphaZ": self._wrapped.AlfaZ,
        }


class IAxisVMMaterials(AxisVMModelItems):
    """Wrapper for the `IAxisVMMaterials` COM interface."""

    __itemcls__ = IAxisVMMaterial

    def _get_attrs(self):
        """Return the representation methods (internal helper)."""
        attrs = []
        attrs.append(("N Materials", self.Count, "{}"))
        return attrs
