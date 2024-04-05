# -*- coding: utf-8 -*-
from time import sleep

from .axapp import IAxisVMApplication as AxApp


__all__ = ["start_AxisVM"]


def start_AxisVM(
    *args, join=False, visible=None, daemon=False, wrap=True, **kwargs
) -> AxApp:
    """Returns an interface to a new, or an existing AxisVM application.

    If the argument `join` is True, an attempt is made to connect to an
    already running instance. If there is a running instance but `join`
    is False, that instance gets destroyed and a new one will be created.

    If the first argument is a valid path to an AxisVM model file, it gets
    opened.

    Parameters
    ----------
    join : boolean, Optional
        Controls what to do if there is an already running instance
        to connect to. Default is False.

        This is only available from X6r2. For versions prior to this,
        `join=True` has no effect and a new instance is created every time.

    visible : boolean or None, Optional
        Sets the visibility of the AxisVM application, while a None\n
        value takes no effect. Default is None.

    daemon : boolean, Optional
        Controls the behaviour of the COM interface. Default is False.

        Assuming that `axapp` is a COM interface to an AxisVM application,
        `daemon=True` is equivalent to

        >>> from axisvm.com.tlb import acEnableNoWarning, lbFalse, lbTrue
        >>> axapp.CloseOnLastReleased = lbTrue
        >>> axapp.AskCloseOnLastReleased = lbFalse
        >>> axapp.AskSaveOnLastReleased = lbFalse
        >>> axapp.ApplicationClose = acEnableNoWarning

    wrap : boolean, Optional
        Wraps the returning object if True, returns the raw object otherwise.
        Default is True.

    Returns
    -------
    :class:`axisvm.com.axapp.AxApp`
        A python wrapper around an IAxisVMApplication instance.

    Examples
    --------
    >>> from axisvm.com.client import start_AxisVM
    >>> axvm = start_AxisVM(visible=True, daemon=True)

    See Also
    --------
    :func:`axisvm.com.tlb.wrap_axisvm_tlb`
    :func:`axisvm.com.tlb.find_axisvm_tlb`

    """
    axapp = _find_AxisVM()
    if axapp is not None and not join:
        try:
            axapp.Quit()
            del axapp
        except Exception:
            pass
        finally:
            axapp = None
    if axapp is None:
        from comtypes.client import CreateObject

        axapp = CreateObject("AxisVM.AxisVMApplication")
    if axapp is not None:
        _init_AxisVM(axapp, daemon=daemon, visible=visible, **kwargs)

    if wrap:
        res = AxApp(wrap=axapp)
        if len(args) > 0 and isinstance(args[0], str):
            res.model = args[0]
        return res
    else:
        if len(args) > 0 and isinstance(args[0], str):
            _from_file(axapp, args[0])
        return axapp


def _init_AxisVM(axapp, *args, visible=None, daemon=False, **kwargs):
    while not axapp.Loaded:
        sleep(0.1)
    if isinstance(visible, bool):
        axapp.Visible = 1 if visible else 0
    _init_daemon(axapp) if daemon else None


def _init_daemon(axapp, *args, **kwargs):
    from axisvm.com.tlb import lbTrue as true, lbFalse as false, acEnableNoWarning

    axapp.CloseOnLastReleased = true
    axapp.AskCloseOnLastReleased = false
    axapp.AskSaveOnLastReleased = false
    axapp.ApplicationClose = acEnableNoWarning


def _from_file(axapp, path):
    try:
        model = axapp.Models.New()
        model.LoadFromFile(path)
    except Exception as e:
        raise e


def _find_AxisVM():
    try:
        from comtypes.client import GetActiveObject

        return GetActiveObject("AxisVM.AxisVMApplication")
    except Exception:
        return None
