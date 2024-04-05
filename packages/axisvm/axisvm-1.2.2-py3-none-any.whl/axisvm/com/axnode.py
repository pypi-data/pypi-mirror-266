# -*- coding: utf-8 -*-
from typing import List, Union

import axisvm.com.tlb as axtlb

from .core.wrap import AxisVMModelItem, AxisVMModelItems
from .axsurface import SurfaceMixin


__all__ = ["IAxisVMNode", "IAxisVMNodes"]


class IAxisVMNode(AxisVMModelItem, SurfaceMixin):
    """Wrapper for the `IAxisVMNode` COM interface."""

    ...


class IAxisVMNodes(AxisVMModelItems, SurfaceMixin):
    """Wrapper for the `IAxisVMNodes` COM interface."""

    __itemcls__ = IAxisVMNode

    def get_record(
        self, *args, interactive: bool = False, **kwargs
    ) -> Union[axtlb.RNode, List[axtlb.RNode]]:
        """
        Returns a list of node records or a single record, which can be specified 
        by keyword arguments. It can be used to turn an arbitrary specification
        of nodes in an embedded situation into a list of node recirds.
        For that reason it includes trivial keys. Individual elements
        can be specified, but the result is always a list. If there are
        no valid specifiers, then
            (1) if argument 'all' is provided, all of the nodes of the
                model are returned
            (2) if interactive == True, function either gets the selected
                nodes from AxisVM, or if there is none, a selection \
                dialog shows up in AxisVM and the function is called again \
                with valid specifiers emerging from any of these scenarios.

        Parameters
        ----------
        **kwargs : dict, Optional
            Possible keyword arguments:
            
            * node : a single node, returns a sigle record
            * nodes : a list of nodes, returns a list of records
            * ID : int, a single nodeID
            * IDs : list of int, a sequence of nodeIDs
            * UID : int, a single nodeUID
            * UIDs : list of int, a sequence of nodeUIDs

        Returns
        -------
        Union[axtlb.RNode, List[axtlb.RNode]]
            A single record, or a list of records, depending on the input.    
        """
        Model = self.model
        nodes = None
        try:
            if "node" in kwargs:
                nodes = [kwargs.pop("node")]
            elif "nodes" in kwargs:
                nodes = kwargs.pop("nodes")
            elif "ID" in kwargs:
                nodes = [Model.Nodes.GetNode(kwargs.pop("ID"))[0]]
            elif "IDs" in kwargs:
                nodes = [Model.Nodes.GetNode(ID)[0] for ID in kwargs.pop("IDs")]
            elif "UID" in kwargs:
                ID = Model.Nodes.IndexOfUID(kwargs.pop("UID"))
                nodes = [Model.Nodes.GetNode(ID)[0]]
            elif "UIDs" in kwargs:
                IDs = [Model.Nodes.IndexOfUID(UID) for UID in kwargs.pop("UIDs")]
                nodes = [Model.Nodes.GetNode(ID)[0] for ID in IDs]
        except Exception:
            raise "Ivalid specification of nodes!"
        finally:
            if nodes is None:
                nodes = self.get_selected(interactive=interactive)
                if nodes is None and "all" in args:
                    nNode = Model.Nodes.Count
                    nodeIDs = [i for i in range(1, nNode + 1)]
                    nodes = self.get_record(IDs=nodeIDs, interactive=False)
            return nodes

    def select(self, clear: bool = True, msg: str = None) -> Union[list, None]:
        """
        Shows up a selectiondialog for nodes in AxisVM and returns the selected
        nodes if succesful or None is nothing is selected.

        Parameters
        ----------
        clear: boolean, Optional
            Clears selection if True. Default is True.
        msg: str, Optional
            The message to show. If not provided, a default message is shown.
            Default is True.
        """
        msg = "Select one or more nodes!" if msg is None else msg
        deletecurrent = 1 if clear else 0
        self.model.app.BringToFront()
        self.model.StartModalSelection(msg, deletecurrent, chr(axtlb.seltNode))
        return self.get_selected(interactive=False)

    def get_selected(
        self, interactive: bool = False, msg: str = None
    ) -> Union[list, None]:
        """
        Returns a dictionary of nodes mapping node indices to node records,
        or None if the selection is invalid.

        Parameters
        ----------
        interactive: bool, Optional
            If nothing is selected when calling this function and this parameter
            is `True`, a selection box appears and nodes can be selected through
            the graphical user interface. If `False`, the function only returns
            a list of nodes if they are already selected when this function is called.
            Default is False.
        msg:str, Optional
            The message to show, only if 'interactive' is `True`. Default is None,
            in which case a default message is shown.
        """
        Model = self.model._wrapped
        try:
            nIDs = Model.Nodes.GetSelectedItemIds()[0]
            return [Model.Nodes.GetNode(nID)[0] for nID in nIDs]
        except Exception:
            if interactive:
                return self.select(clear=True, msg=msg)
            else:
                return None

    def get_indices(self, *args, interactive: bool = False, **kwargs) -> List[int]:
        """
        Returns a list of integers, depending on the arguments.
        It can be used to turn an arbitrary specification of nodes into a list
        of indices. Individual items can be specified, but the result is always a list.
        If there are no valid specifiers, the function either gets the selected nodes
        from AxisVM, or if there is none, a selection dialog shows up in
        AxisVM and the function is called again with valid specifiers
        emerging from any of these scenarios.

        Possible keys and values

        * node : a single node record
        * nodes : a list of node records
        * ID : int, a single node index
        * IDs : [int], a sequence of node indices
        * UID : int, a single unique node index
        * UIDs : [int], a sequence of unique node indices

        Note
        ----
        The call accepts the trivial keys 'ID' and 'IDs' to support automatization,
        where demand for trivial inputs is possible.

        Returns
        -------
        List[int]

        Examples
        --------
        To get indices of nodes from a selection in AxisVM.

        >>> axvm = start_AxisVM(visible=True, daemon=True)
        >>> axvm.model = examples.download_bernoulli_grid()
        >>> axvm.model.Nodes.get_indices()
        """
        nodeIDs = None
        Model = self.model
        try:
            if "node" in kwargs:
                n = kwargs["node"]
                nodeIDs = [Model.Nodes.IndexOf(n.x, n.y, n.z, 1e-8, 1)]
            elif "nodes" in kwargs:
                nodes = kwargs["nodes"]
                nodeIDs = [Model.Nodes.IndexOf(n.x, n.y, n.z, 1e-8, 1) for n in nodes]
            if "ID" in kwargs:
                nodeIDs = [kwargs["ID"]]
            elif "nodeIDs" in kwargs:
                nodeIDs = kwargs["IDs"]
            elif "UID" in kwargs:
                nodeIDs = [Model.Nodes.IndexOfUID(kwargs["UID"])]
            elif "UIDs" in kwargs:
                nodeIDs = [Model.Nodes.IndexOfUID(UID) for UID in kwargs["UIDs"]]
        except Exception:
            raise "Ivalid specification of nodeIDs!"
        finally:
            if nodeIDs is None:
                nodeIDs = self.get_selected_indices(interactive=interactive)
                if nodeIDs is None and "all" in args:
                    nNode = Model.Nodes.Count
                    nodeIDs = [i for i in range(1, nNode + 1)]
            return nodeIDs

    def select_indices(self, clear=True, msg: str = None) -> Union[list, None]:
        """
        Shows up a selectiondialog for nodes in AxisVM and returns the selected
        nodeIDs if succesful.

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
        Model.StartModalSelection(msg, deletecurrent, chr(axtlb.seltNode))
        return self.get_selected_indices(interactive=False)

    def get_selected_indices(self, interactive: bool = False) -> Union[list, None]:
        """
        Returns a list of nodeIDs. The result is always iterable,
        even if it contains only one item.
        """
        Model = self.model
        try:
            return Model.Nodes.GetSelectedItemIds()[0]
        except Exception:
            if interactive:
                return self.select_indices(msg="Select one or more nodes!")
            else:
                return None

    def connected_surfaces(
        self, flatten: bool = False, as_dict: bool = False, **kwargs
    ) -> Union[dict, list]:
        """
        Returns surfaces connected by the specified nodes. For the details of
        specification of nodes see the documentation of :func:`get_indices`.
        If ``as_dict == True``, the result is a dictionary that maps node indices
        to lists of surfaces.
        """
        Model = self.model
        nodeIDs = self.get_indices(**kwargs)
        assert nodeIDs is not None, "Invalid specification of nodes!"
        if as_dict:
            return dict(
                {nID: Model.Nodes.GetConnectedSurfaces(nID)[0] for nID in nodeIDs}
            )
        if flatten:
            surfaces = set()
            for nID in nodeIDs:
                surfaces.update(Model.Nodes.GetConnectedSurfaces(nID)[0])
            return list(surfaces)
        return [Model.Nodes.GetConnectedSurfaces(nID)[0] for nID in nodeIDs]
