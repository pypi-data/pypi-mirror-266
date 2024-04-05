# -*- coding: utf-8 -*-
from typing import Iterable, Union, Tuple, Dict

import numpy as np
from numpy import ndarray as Array
import awkward as ak

from sigmaepsilon.mesh import TopologyArray

import axisvm
from .core.wrap import AxisVMModelItem, AxisVMModelItems
from .core.utils import RMatrix3x3toNumPy
from .attr import AxisVMAttributes
from .axline import get_line_attributes


class IAxisVMMember(AxisVMModelItem):
    """Wrapper for the `IAxisVMMember` COM interface."""

    @property
    def tr(self) -> Array:
        """
        Returns the transformation matrix of the member as a NumPy array.
        """
        return self.transformation_matrix()

    @property
    def frame(self) -> Array:
        """
        Returns the local coordinate frame of the member as a NumPy array.
        """
        return self.transformation_matrix()

    @property
    def attributes(self):
        """
        Returns the attributes of the member.
        """
        return self.parent.get_attributes(self.Index)

    @property
    def member_attributes(self):
        """
        Returns the member attributes of the member.
        """
        return self.parent.get_member_attributes(self.Index)

    def topology(self) -> TopologyArray:
        lIDs = np.array(self.GetLines()[0]).flatten()
        lines = self.model.Lines.wrapped

        def foo(i):
            return [lines.Item[i].StartNode, lines.Item[i].EndNode]

        return TopologyArray(np.squeeze(np.array(list(map(foo, lIDs)), dtype=int)))

    def get_line_id_and_line_section_id(
        self, analysis_type: int, member_section_id: int
    ) -> Tuple[int]:
        """
        Parameters
        ----------
        analysis_type: int
            The type of the analysis as an `EAnalisysType` value.
        member_section_id: int
            The section index of the member.

        Returns
        -------
        Tuple[int]
            The index of the line and the line section.
        """
        result = self.wrapped.GetLineIDAndLineSectionID(
            analysis_type, member_section_id
        )
        if result[-1] < 0:
            raise Exception(f"Error code: {result[-1]}")
        else:
            return result[:2]

    def _get_attrs(self) -> list:
        """Return the representation methods (internal helper)."""
        attrs = []
        attrs.append(("Name", self.Name, "{}"))
        attrs.append(("Index", self.Index, "{}"))
        attrs.append(("UID", self._wrapped.UID, "{}"))
        attrs.append(("N Lines", len((self.GetLines()[0])), "{}"))
        attrs.append(("Length", self.Length, axisvm.FLOAT_FORMAT))
        attrs.append(("Volume", self.Volume, axisvm.FLOAT_FORMAT))
        attrs.append(("Weight", self.Weight, axisvm.FLOAT_FORMAT))
        return attrs

    def transformation_matrix(self) -> Array:
        return RMatrix3x3toNumPy(self.GetTrMatrix()[0])

    def record(self):
        return self.parent.records(self.Index)


class IAxisVMMembers(AxisVMModelItems):
    """Wrapper for the `IAxisVMMembers` COM interface."""

    __itemcls__ = IAxisVMMember

    @property
    def tr(self) -> Array:
        return self.transformation_matrices()

    @property
    def frames(self) -> Array:
        return self.transformation_matrices()

    @property
    def attributes(self):
        return self.get_attributes()

    @property
    def member_attributes(self):
        return self.get_member_attributes()

    def get_connected_member_ids(
        self,
        nodeIDs: Union[int, Iterable[int]] = None,
        return_relative_indices: bool = True,
    ) -> Dict[int, Union[Iterable[int], Tuple[Iterable[int], Iterable[int]]]]:
        """
        Returns the indices of the members connected by one or more nodes, and optionally
        the relative node indices of the connected members.

        Parameters
        ----------
        nodeIDs: Union[int, Iterable[int]], Optional
            The indices of the nodes for which the connected members should be returned.
            If not provided, connectivity information for all members are returned.
            Default is None.
        return_relative_indices: bool, Optional
            If `True` relative indices (0 for stargin node, 1 for ending node) are also returned.
            Default is True.

        Returns
        -------
        Dict[int, Union[Iterable[int], Tuple[Iterable[int], Iterable[int]]]]
            A dictionary where the keys are the provided node IDs, and the values are
            the indices, optionally as a tuple with the relative node indices of the
            connected members being the second item in each tuple.

        See also
        --------
        :func:`get_connected_members`
        """
        single_item = isinstance(nodeIDs, int)
        nodeIDs = [nodeIDs] if single_item else nodeIDs
        topo = self.starting_and_ending_nodes()

        result = {}
        for node_id in nodeIDs:
            member_ids, relative_node_ids = np.where(topo == node_id)
            if return_relative_indices:
                result[node_id] = member_ids + 1, relative_node_ids
            else:
                result[node_id] = member_ids + 1

        return result

    def get_connected_members(
        self, *args, **kwargs
    ) -> Dict[
        int,
        Union[Iterable[IAxisVMMember], Tuple[Iterable[IAxisVMMember], Iterable[int]]],
    ]:
        """
        Returns the members connected by one or more nodes, and optionally
        the relative node indices of the connected members.

        All the parameters are forwarded to :func:`get_connected_member_ids`, refer its
        documentation for the possible arguments.

        Returns
        -------
        Dict[int, Union[Iterable[IAxisVMMember], Tuple[Iterable[IAxisVMMember], Iterable[int]]]]
            A dictionary where the keys are the provided node IDs, and the values are
            the members, optionally as a tuple with the relative node indices of the
            connected members being the second item in each tuple.

        See also
        --------
        :func:`get_connected_member_ids`
        """
        members = self.wrapped
        conn: dict = self.get_connected_member_ids(*args, **kwargs)

        result = {}
        for key, value in conn.items():
            if isinstance(value, tuple):
                member_ids, relative_node_ids = value
            else:
                member_ids, relative_node_ids = value, None

            _members = [self[i] for i in member_ids]

            if relative_node_ids is not None:
                result[key] = _members, relative_node_ids
            else:
                result[key] = members

        return result

    def topology(self, *args, i: int = None) -> TopologyArray:
        """
        Returns the topology of the lines of the members of the model.

        Parameters
        ----------
        *args: tuple, Optional
            Member indices. If specified, only the topology of these members are returned.
        i: int, Optional
            The id of the member for which the topology should be returned.

        Returns
        -------
        sigmaepsilon.mesh.TopologyArray
        """
        axm = self.model.wrapped
        lines = axm.Lines
        members = self.wrapped
        i = i if len(args) == 0 else list(args)
        if isinstance(i, int):
            inds = [i]
        if isinstance(i, np.ndarray):
            inds = i
        else:
            if isinstance(i, Iterable):
                inds = np.array(i, dtype=int)
            else:
                inds = np.array(list(range(members.Count))) + 1

        def fnc(i):
            return list(members.Item[i].GetLines()[0])

        nodelist = list(map(fnc, inds))
        arr = TopologyArray(ak.Array(nodelist))
        lIDs = arr.flatten()

        def fnc(i):
            return [lines.Item[i].StartNode, lines.Item[i].EndNode]

        return TopologyArray(ak.Array(list(map(fnc, lIDs))))

    def starting_and_ending_nodes(self, *args, i: int = None) -> Array:
        """
        Returns indices of starting and ending nodes of the members.

        Parameters
        ----------
        *args: tuple, Optional
            Member indices. If specified, only the topology of these members are returned.
        i: int, Optional
            The id of the member for which the topology should be returned.

        Returns
        -------
        numpy.ndarray
        """
        members = self.wrapped
        i = i if len(args) == 0 else list(args)
        if isinstance(i, int):
            inds = [i]
        if isinstance(i, np.ndarray):
            inds = i
        else:
            if isinstance(i, Iterable):
                inds = np.array(i, dtype=int)
            else:
                inds = np.array(list(range(members.Count))) + 1
        nodes = [[m.StartNode, m.EndNode] for m in [members.Item[i] for i in inds]]
        return np.array(nodes, dtype=int)

    def transformation_matrices(self, *args, i=None) -> Array:
        m = self._wrapped
        i = i if len(args) == 0 else args[0]
        if isinstance(i, int):
            return RMatrix3x3toNumPy(self[i].GetTrMatrix()[0])
        if isinstance(i, np.ndarray):
            ids = i
        else:
            if isinstance(i, Iterable):
                ids = np.array(i, dtype=int)
            else:
                ids = np.array(list(range(m.Count))) + 1
        rec = list(map(lambda i: m.Item[i].GetTrMatrix()[0], ids))
        return np.array(list(map(RMatrix3x3toNumPy, rec)), dtype=float)

    def _get_attributes_raw(self, *args, i=None, **kwargs) -> Iterable:
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
        return self.BulkGetMembers(ids)

    def get_member_attributes(self, *args, **kwargs) -> AxisVMAttributes:
        return get_line_attributes(self, *args, **kwargs)

    def get_attributes(self, *args, **kwargs) -> AxisVMAttributes:
        return self.get_member_attributes(*args, **kwargs)

    def records(self, *args, **kwargs) -> AxisVMAttributes:
        return self.get_member_attributes(*args, raw=True, **kwargs)
