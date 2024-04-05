# -*- coding: utf-8 -*-
from sigmaepsilon.core.wrapping import Wrapper
from typing import Callable, Iterable, Any


__all__ = ["AxWrapper", "AxisVMModelItem", "AxisVMModelItems"]


NoneType = type(None)


class AxItemCollection(list):
    def __getattribute__(self, attr):
        if hasattr(self[0], attr):
            _attr = getattr(self[0], attr)
            if isinstance(_attr, Callable):
                getter = lambda i: getattr(i, attr)
                funcs = map(getter, self)

                def inner(*args, **kwargs):
                    return list(map(lambda f: f(*args, **kwargs), funcs))

                return inner
            else:
                return list(map(lambda i: getattr(i, attr), self))
        else:
            return super().__getattribute__(attr)


class AxWrapper(Wrapper):
    __itemcls__ = None
    __collectioncls__ = None

    def __init__(self, *args, **kwargs):
        self.__has_items = False
        super().__init__(*args, **kwargs)

    def wrap(self, obj=None):
        if obj is not None:
            if hasattr(obj, "Item"):
                self.__has_items = True
            else:
                self.__has_items = False
                self.__itemcls__ = None
        super().wrap(obj)

    @property
    def Item(self):
        if self.__has_items:
            return self
        else:
            raise AttributeError("Object {} has no attribute 'Item'.".format(self))

    def __repr__(self) -> str:
        return self._wrapped.__repr__()

    def __len__(self):
        if hasattr(self._wrapped, "Count"):
            return self._wrapped.Count
        else:
            raise AttributeError(
                "Object {} has no concept of length.".format(self._wrapped)
            )

    def __iter__(self):
        for i in range(1, self.Count + 1):
            yield self[i]

    def __getattr__(self, attr):
        res = super().__getattr__(attr)
        if hasattr(res, "Item"):
            return AxWrapper(wrap=res)
        return res

    def __setattr__(self, __name: str, __value: Any) -> None:
        if "_wrapped" in self.__dict__:
            if self._wrapped is not None and hasattr(self._wrapped, __name):
                return setattr(self._wrapped, __name, __value)
        return super().__setattr__(__name, __value)

    def __getitem__(self, ind):
        if self.__has_items:
            cls = AxWrapper if self.__itemcls__ is None else self.__itemcls__
            ccls = (
                AxItemCollection
                if self.__collectioncls__ is None
                else self.__collectioncls__
            )
            if isinstance(ind, slice):
                axobj = self._wrapped
                item = lambda i: cls(wrap=axobj.Item[i], parent=self)
                start, stop, step = ind.start, ind.stop, ind.step
                start = 1 if start == None else start
                stop = axobj.Count + 1 if stop == None else stop
                step = 1 if step == None else step
                inds = list(range(start, stop, step))
                if min(inds) < 0:
                    N = self._wrapped.Count + 1
                    foo = lambda i: i if i > 0 else N + i
                    inds = map(foo, inds)
                res = list(map(item, inds))
                if len(res) == 1:
                    return res[0]
                return ccls(res)
            elif isinstance(ind, Iterable):
                axobj = self._wrapped
                item = lambda i: cls(wrap=axobj.Item[i], parent=self)
                res = [item(i) for i in ind]
                if len(res) == 1:
                    return res[0]
                return ccls(res)
            else:
                if ind < 0:
                    ind = self._wrapped.Count + 1 + ind
                return cls(wrap=self._wrapped.Item[ind], parent=self)
        else:
            try:
                return super().__getitem__(ind)
            except Exception:
                try:
                    return self._wrapped.__getitem__(ind)
                except Exception:
                    raise TypeError(
                        "'{}' object is not "
                        "subscriptable".format(self.__class__.__name__)
                    )

    def _get_attrs(self):
        """Return the representation methods (internal helper)."""
        return []

    def head(self, display=True, html: bool = None):
        """Return the header stats of this dataset.

        If in IPython, this will be formatted to HTML. Otherwise
        returns a console friendly string.

        Parameters
        ----------
        display: bool, optional
            Display this header in iPython.
        html: bool, optional
            Generate the output as HTML.

        Returns
        -------
        str
            Header statistics.
        """
        # Generate the output
        attrs = self._get_attrs()
        if len(attrs) == 0:
            return type(self).__name__
        if html:
            fmt = ""
            # HTML version
            fmt += "\n"
            fmt += "<table>\n"
            fmt += f"<tr><th>{type(self).__name__}</th><th>Information</th></tr>\n"
            row = "<tr><td>{}</td><td>{}</td></tr>\n"
            # now make a call on the object to get its attributes as a list of len 2 tuples
            for attr in attrs:
                try:
                    fmt += row.format(attr[0], attr[2].format(attr[1]))
                except Exception:
                    pass
            fmt += "</table>\n"
            fmt += "\n"
            if display:
                from IPython.display import HTML, display as _display

                _display(HTML(fmt))
                return
            return fmt
        # Otherwise return a string that is Python console friendly
        fmt = f"{type(self).__name__} ({hex(id(self))})\n"
        # now make a call on the object to get its attributes as a list of len 2 tuples
        row = "  {}:\t{}\n"
        for attr in attrs:
            try:
                fmt += row.format(attr[0], attr[2].format(*attr[1]))
            except:
                fmt += row.format(attr[0], attr[2].format(attr[1]))
        return fmt

    def _repr_html_(self) -> str:
        """
        Return a pretty representation for Jupyter notebooks.

        It includes header details and information about all arrays.

        """
        return self.head(display=False, html=True)

    def __repr__(self) -> str:
        """Return the object representation."""
        return self.head(display=False, html=False)

    def __str__(self) -> str:
        """Return the object string representation."""
        return self.head(display=False, html=False)


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
        self.model = model

    @property
    def Items(self):
        return map(lambda i: self[i + 1], range(self.Count))
