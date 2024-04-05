# -*- coding: utf-8 -*-
from typing import Union, Tuple
from .core.wrap import AxWrapper
from .core.utils import _LoadLevelOrModeShapeOrTimeStep


class AxisVMResultItem(AxWrapper):
    """
    Base wrapper class for interfaces of items, such as individual
    lines, surfaces, etc.

    """

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    @property
    def model(self) -> AxWrapper:
        return self.parent.model

    def _get_case_or_component(
        self,
        *,
        case: Union[str, int] = None,
        combination: Union[str, int] = None,
        load_case_id: int = None,
        load_combination_id: int = None,
        **__,
    ) -> Tuple[Union[None, int]]:
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
        return load_case_id, load_combination_id

    def config(
        self,
        *args,
        displacement_system: int = None,
        load_level: int = None,
        mode_shape: int = None,
        time_step: int = None,
        **kwargs,
    ):
        LoadCaseId, LoadCombinationId = self._get_case_or_component(*args, **kwargs)
        resobj = self._wrapped

        if isinstance(displacement_system, int):
            resobj.DisplacementSystem = displacement_system

        if LoadCaseId is not None:
            resobj.LoadCaseId = LoadCaseId

        if LoadCombinationId is not None:
            resobj.LoadCombinationId = LoadCombinationId

        LoadLevelOrModeShapeOrTimeStep = _LoadLevelOrModeShapeOrTimeStep(
            load_level=load_level,
            mode_shape=mode_shape,
            time_step=time_step,
            return_none=True,
        )
        if LoadLevelOrModeShapeOrTimeStep is not None:
            resobj.LoadLevelOrModeShapeOrTimeStep = LoadLevelOrModeShapeOrTimeStep


class IAxisVMDisplacements(AxisVMResultItem):
    """Wrapper for the `IAxisVMDisplacements` COM interface."""

    ...


class IAxisVMForces(AxisVMResultItem):
    """Wrapper for the `IAxisVMForces` COM interface."""

    ...


class IAxisVMStresses(AxisVMResultItem):
    """Wrapper for the `IAxisVMStresses` COM interface."""

    ...


class IAxisVMResults(AxWrapper):
    """Wrapper for the `IAxisVMResults` COM interface."""

    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    @property
    def Displacements(self) -> IAxisVMDisplacements:
        return IAxisVMDisplacements(parent=self, wrap=self._wrapped.Displacements)

    @property
    def Forces(self) -> IAxisVMForces:
        return IAxisVMForces(parent=self, wrap=self._wrapped.Forces)

    @property
    def Stresses(self) -> IAxisVMStresses:
        return IAxisVMStresses(parent=self, wrap=self._wrapped.Stresses)
