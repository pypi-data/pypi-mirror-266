# -*- coding: utf-8 -*-
from typing import Tuple, Union, Optional
import ctypes
from ctypes import Structure

from .core.wrap import AxWrapper


__all__ = ["IAxisVMRCBeamDesign"]


class IAxisVMRCBeamDesign(AxWrapper):
    """
    Wrapper for the `IAxisVMRCBeamDesign` COM interface.
    """

    def GetDesignParameters(
        self, *args, record_type: Optional[Union[Structure, None]] = None, **kwargs
    ) -> Tuple[Structure, Structure]:
        """
        Returns the parameters used for the design of reinforced
        concrete columns.

        Parameters
        ----------
        record_type: ctypes.Structure or None, Optional
            The type of the record like `RRCBeamDesignParameters_EC` or
            `RRCBeamDesignParameters_DIN`, etc. If not specified, a list
            of unsigned 8-bit integers is returned and you need to cast these
            values manually to the appropriate record type. Default is None.

        Note
        ----
        If you want to call the original API endpoint, leave the parameter
        'record_type' unspecified (None).
        """
        (
            beam_design_parameters,
            design_code_parameters,  # this is a list of c_ubyte values
            error_code,
        ) = self._wrapped.GetDesignParameters(*args, **kwargs)

        if error_code != 1:  # pragma no cover
            raise Exception(f"Something went wrong. The error code is {error_code}")

        if record_type is not None:
            # Convert the list of c_ubyte values back into the structure
            buffer = (ctypes.c_ubyte * len(design_code_parameters))(
                *design_code_parameters
            )
            design_code_parameters = ctypes.cast(
                buffer, ctypes.POINTER(record_type)
            ).contents

        return beam_design_parameters, design_code_parameters

    def SetDesignParameters(
        self, RCBeamDesignParameters: Structure, DesignCodeParameters: Structure
    ) -> int:
        """
        Sets the design parameters related to teh design of reinforced concrete beams.

        Parameters
        ----------
        RCBeamDesignParameters
            An instance of `RCBeamDesignParameters`.
        DesignCodeParameters
            A record, according to the design standard set for the model. For instance, if the
            standard is Eurocode, the record would be an instance of `RRCBeamDesignParameters_EC`,
            if the standard is Eurocode-DIN, it would be an instance of `RRCBeamDesignParameters_DIN`,
            etc.

        Returns
        -------
        int
            The return value of the original API call. The returned integer is 1 if the call was
            succesful, otherwise it is an error code.
        """
        # create a byte array from the structure
        buffer = (
            ctypes.c_ubyte * ctypes.sizeof(DesignCodeParameters)
        ).from_buffer_copy(DesignCodeParameters)
        ubyte_list = list(buffer)
        return self._wrapped.SetDesignParameters(RCBeamDesignParameters, ubyte_list)[-1]
