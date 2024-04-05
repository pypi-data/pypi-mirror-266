# -*- coding: utf-8 -*-
from .core.wrap import AxisVMModelItems


__all__ = ["IAxisVMCalculation"]


class IAxisVMCalculation(AxisVMModelItems):
    """Wrapper for the `IAxisVMCalculation` COM interface."""

    def LinearAnalysis(
        self,
        *args,
        interact: bool = False,
        show: bool = False,
        autocorrect: bool = True,
    ):
        """
        Performs a linear analysis on the structure.

        Parameters
        ----------
        *args : tuple, Optional
            If there is a positional argument, it is considered as a valid argument
            to the `LinearAnalysis` method of the `IAxisVMCalculation` interface, and
            all other paramaters are ignored.

        interact : bool, Optional.
            If True, the user has to interact with the program to answer questions
            arising during the analysis. Default is False.

        show : bool, Optional.
            Whether the calculation window should be visible or not.
            Default is False.

        autocorrect : bool, Optional.
            If True, AxisVM tries to correct problems automatically during the analysis.
            Default is True.

        """
        if len(args) > 0 and isinstance(args[0], int):
            itype = args[0]
        else:
            import axisvm.com.tlb as axtlb

            if interact:
                itype = axtlb.cuiUserInteraction
            else:
                if show and autocorrect:
                    itype = axtlb.cuiNoUserInteractionWithAutoCorrect
                elif not show and autocorrect:
                    itype = axtlb.cuiNoUserInteractionWithoutAutoCorrect
                elif not show and autocorrect:
                    itype = axtlb.cuiNoUserInteractionWithAutoCorrectNoShow
                elif not show and not autocorrect:
                    itype = axtlb.cuiNoUserInteractionWithoutAutoCorrectNoShow
                else:
                    raise NotImplementedError
        return self._wrapped.LinearAnalysis(itype)
