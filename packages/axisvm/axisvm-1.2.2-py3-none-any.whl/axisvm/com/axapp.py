# -*- coding: utf-8 -*-
import os
from typing import Union

from .core.wrap import AxWrapper
from .axmodel import IAxisVMModel, IAxisVMModels
from .axcatalog import IAxisVMCatalog


class IAxisVMApplication(AxWrapper):
    """
    Wrapper for the `IAxisVMApplication` COM interface.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._model = IAxisVMModel(wrap=self._wrapped.Models.Item[1], app=self)
        except Exception:
            self.new_model(**kwargs)

    @property
    def app(self) -> object:
        """
        Returns a pointer object to the `IAxisVMApplication` COM interface of
        the embedding AxisVM instance.
        """
        return self._wrapped

    @property
    def Models(self) -> IAxisVMModels:
        """Returns a pointer object to the `IAxisVMModels` COM interface."""
        return IAxisVMModels(app=self, wrap=self._wrapped.Models)

    @property
    def model(self) -> IAxisVMModel:
        """
        Returns a pointer object to the `IAxisVMModel` COM interface of the
        active model in AxisVM.

        Notes
        -----
        As of now, AxisVM only supports one active model at once, but this may
        change later. Nontheless, the interface is designed as if it was able to handle
        multiple active models.
        """
        return self._model

    @model.setter
    def model(self, value: Union[int, str]):
        """
        Sets the active model.
        """
        if isinstance(value, int):
            self._model = IAxisVMModel(wrap=self._wrapped.Models.Item[value], app=self)
        elif isinstance(value, str):
            if os.path.exists(value):
                if self._model is None:
                    self.new_model()
                self._model.LoadFromFile(value)
            else:
                raise FileNotFoundError("File {} not found!".format(value))
        else:
            raise RuntimeError("Invalid input : {}!".format(value))

    def new_model(self) -> IAxisVMModel:
        """
        Creates new model and returns a pointer object to its `IAxisVMModel`
        COM interface. Optinally, it saves the model, given that a valid file
        path is provided.
        """
        self.model = self._wrapped.Models.New()
        return self._model

    def UnLoadCOMclients(self) -> int:
        """
        Stops, unloads and releases memory taken by COM clients (addons, plugins
        and addon-plugins), then closes the application.

        Returns
        -------
        int
            Returns 1 if succesful.
        """
        return self._wrapped.UnLoadCOMclients()

    def BringToFront(self) -> int:
        """
        Bring AxisVM above other opened applications.

        Returns
        -------
        int
            1 if succesful, 0 otherwise.
        """
        return self._wrapped.BringToFront()

    def ChangeUnitSystem(self, name: str) -> int:
        """
        Bring AxisVM above other opened applications.

        Returns
        -------
        int
            1 if succesful, 0 otherwise.
        """
        pass

    def CustomFunction(self, customId: int, jsonIN: str, jsonOUT: str):
        """
        This function was introduced to allow for new functions and features which will
        be fully implemented in a future version of the COM server.

        Parameters
        ----------
        customId: str
            Custom function index.
        jsonIN: str
            Input parameters in JSON format.

        jsonOUT: str
            Output parameters in JSON format.

        Returns
        -------
        jsonOUT: str
            Output parameters in JSON format.
        int
            Number of fields in JSON output if call is successful, otherwise an error code
            `errJSONpropertyMissing` or `errNotImplemented`.
        """
        r = self._wrapped.CustomFunction(customId, jsonIN, jsonOUT)
        return jsonOUT, r

    def DisableMainForm(self):
        """
        Disable all controls on AxisVM form including the selection toolbar.
        """
        return self._wrapped.EnableMainForm()

    def EnableMainForm(self):
        """
        Enable all controls on AxisVM form.
        """
        return self._wrapped.EnableMainForm()

    def HandleMessages(self):
        """
        Handles the messages in AxisVM and the COM client while the COM client is
        blocking the thread being executed. It is used as the body of a loop, that will
        continue to run till an external event sets a flag. The flag is set in the COM
        client usually through an event such as
        IAxisVMModelsEvents.SelectionProcessingChanged, when for example it is
        called with NewStatus = false (signalling the fact that the user has ended the
        selection process). While the thread being executed is blocked, the COM client
        will still receive events indirectly through HandleMessages, making it possible
        to process those events and ultimately to set the flag that will unblock the
        thread which was blocked through the loop.
        """
        return self._wrapped.HandleMessages()

    def MessageDlg(self, title: str, message: str, dlgtype, buttons: int) -> int:
        """
        Shows a message dialog in AxisVM.

        Parameters
        ----------
        title: str
            Title of the dialog window.
        message: str
            Message text of the dialog window.
        dlgtype: `EMessageDialogType`
            Dialog type.
        buttons: int
            This value can be calculated by adding up the `EMessageDialogButton` values
            of the required buttons( e.g. for showing YES and NO buttons; values is:
            mdbNo + mdbYes).

        Returns
        -------
        int
            The value of the button the user clicked
        """
        return self._wrapped.MessageDlg(title, message, dlgtype, buttons)

    def Quit(self) -> None:
        """
        Stops, unloads and releases memory taken by COM clients (addons, plugins
        and addon-plugins), releases the Python resources associated with the COM connection,
        then closes the application.
        """
        self._wrapped.Quit()
        delattr(self, "_wrapped")

    @property
    def ApplicationClose(self) -> int:
        """
        Determines how AxisVM should close if other clients are connected; if it
        should show a message or disable AxisVM closing while COM client runs.

        Read and write property.

        Returns
        -------
        int
        """
        return self._wrapped.ApplicationClose

    @ApplicationClose.setter
    def ApplicationClose(self, value=None):
        """
        Determines how AxisVM should close if other clients are connected; if it
        should show a message or disable AxisVM closing while COM client runs.

        Parameters
        ----------
        value: `EApplicationClose`
            See the docs of `EApplicationClose` for the details.
        """
        assert value is not None
        self._wrapped.ApplicationClose = value

    @property
    def AskCloseOnLastReleased(self) -> int:
        """
        Determines whether the COM server shutdown displays a query to close the
        AxisVM application as well.

        Read and write property

        Returns
        -------
        int
        """
        return self._wrapped.AskCloseOnLastReleased

    @AskCloseOnLastReleased.setter
    def AskCloseOnLastReleased(self, value: bool = None):
        """
        Determines whether the COM server shutdown displays a query to close the
        AxisVM application as well.

        Parameters
        ----------
        value: bool
        """
        assert isinstance(value, bool)
        self._wrapped.AskCloseOnLastReleased = value

    @property
    def AskSaveOnLastReleased(self) -> int:
        """
        If True, on any attempt to shutdown the COM server a dialog window pops up,
        to warn us to save our model.

        Read and write property

        Notes
        -----
        The model should be saved after modification or if newer version of
        AxisVM is used.
        """
        return self._wrapped.AskSaveOnLastReleased

    @AskSaveOnLastReleased.setter
    def AskSaveOnLastReleased(self, value: bool = None):
        """
        If True, on any attempt to shutdown the COM server a dialog window pops up,
        to warn us to save our model.
        """
        assert isinstance(value, bool)
        self._wrapped.AskSaveOnLastReleased = value

    @property
    def AxisVMPlatform(self) -> int:
        """
        Get AxisVM version type (32/64bit).

        Returns
        -------
        int
            * 32 bit AxisVM -> 0
            * 64 bit AxisVM -> 1
        """
        return self._wrapped.AxisVMPlatform

    @property
    def Catalog(self) -> IAxisVMCatalog:
        """
        Get AxisVM catalog interface for standard materials and cross-sections.
        """
        return IAxisVMCatalog(wrap=self._wrapped.Catalog)

    @property
    def LTWH(self):
        L, T, W, H = (
            self.MainFormWindowLeft,
            self.MainFormWindowTop,
            self.MainFormWindowWidth,
            self.MainFormWindowHeight,
        )
        return L, T, W, H

    def _get_attrs(self):
        """Return the representation methods (internal helper)."""
        attrs = []
        platform = "32" if self.AxisVMPlatform == 0 else "64"
        platform += " bit"
        attrs.append(("AxisVM Platform", platform, "{}"))
        version = "{} {}".format(self.LibraryMajorVersion, self.LibraryMinorVersion)
        attrs.append(("AxisVM Version", self.Version, "{}"))
        attrs.append(("Type Library Version", version, "{}"))
        return attrs
