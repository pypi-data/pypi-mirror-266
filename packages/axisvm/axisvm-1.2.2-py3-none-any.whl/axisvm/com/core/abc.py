# -*- coding: utf-8 -*-
from .wrap import AxWrapper

__all__ = ["AxisVMModelItem", "AxisVMModelItems"]


NoneType = type(None)


class AxisVMModelItem(AxWrapper):
    """
    Base wrapper class for interfaces of items, such as individual
    lines, surfaces, etc.

    """

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    @property
    def model(self):
        return self.parent.model

    @property
    def Index(self):
        return self.parent.IndexOfUID[self.UID]


class AxisVMModelItems(AxWrapper):
    """
    Base wrapper class for interfaces of containers of items, such as
    collections of lines, surfaces, etc.

    """

    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = model

    @property
    def model(self):
        return self._model
