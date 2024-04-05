from typing import Union

import axisvm.com.tlb as axtlb

from .core.wrap import AxisVMModelItem, AxisVMModelItems

__all__ = ["IAxisVMNodalSupport", "IAxisVMNodalSupports"]


class IAxisVMNodalSupport(AxisVMModelItem):
    """Wrapper for the `IAxisVMNodalSupport` COM interface."""

    ...


class IAxisVMNodalSupports(AxisVMModelItems):
    """Wrapper for the `IAxisVMNodalSupports` COM interface."""

    __itemcls__ = IAxisVMNodalSupport
    
    def get_selected_indices(self, interactive: bool = False) -> Union[list, None]:
        """
        Returns a list of nodeIDs. The result is always iterable,
        even if it contains only one item.
        """
        Model = self.model
        try:
            return Model.NodalSupports.GetSelectedItemIds()[0]
        except Exception:
            if interactive:
                return self.select_indices(msg="Select one or more nodal supports!")
            else:
                return None
            
    def select_indices(self, clear=True, msg: str = None) -> Union[list, None]:
        """
        Shows up a selectiondialog for nodal supports in AxisVM and returns the 
        selected IDs if succesful or None if nothing is selected.

        Parameters
        ----------
        clear: boolean, Optional
            Clears selection state of all entities before the operation if `True`.
            Default is `True`.
        msg: str, Optional
            The message to show. If not provided, a default message is shown.
            Default is `True`.
        """
        if msg is None:
            msg = "Select one or more nodes!"
        Model = self.model
        deletecurrent = 1 if clear else 0
        Model.app.BringToFront()
        Model.StartModalSelection(msg, deletecurrent, chr(axtlb.seltNodalSupport))
        return self.get_selected_indices(interactive=False)