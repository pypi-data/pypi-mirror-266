from abc import ABC, abstractmethod
from typing import Tuple, Optional, Callable
from functools import wraps
import socket
import warnings

# from calscipy.bruker import PrairieLink

from ..configs import HoistedConfig
from ..exceptions import SingletonError
from ..registries import Provider
from ..tools import HAS

# If fast PrairieView implementation is compiled...
try:
    import probe_prairie
except ModuleNotFoundError:
#    warnings.warn("Could not find a compiled probe_prairie library...", UserWarning, stacklevel=2)
#    raise ModuleNotFoundError("Could not find a compiled probe_prairie library..."
#                             "probe_prairie comes pre-compiled for Windows 10+ x64; please raise an issue if you are"
#                              "on a Windows 10+ x64 system. Otherwise, make sure to compile the library!")
    pass


def _format_pv_command(function: Callable) -> Callable:
    @wraps(function)
    def decorator(self, message, *args, **kwargs):
        message += "\r\n"
        message = message.encode()
        return function(self, message, *args, **kwargs)
    return decorator


def _format_pv_response(function: Callable) -> Callable:
    @wraps(function)
    def decorator(self, *args, **kwargs):
        response = function(self, *args, **kwargs).decode()
        response = response.split("\r\n")
        return response[1]
    return decorator


@Provider()
class Microscope:

    __instance = None

    def __new__(cls: "Microscope", *args, **kwargs) -> "Microscope":
        if HAS(cls.__instance):
            raise SingletonError(cls)
        else:
            cls.__instance = super(Microscope, cls).__new__(cls)
        return cls.__instance

    def __init__(self,
                 config: Optional["HoistedConfig"] = None,
                 software: str = "PrairieView",
                 realtime_mode: bool = False,
                 motion_correction: bool = False,
                 identify_rois: bool = False,
                 extract_fluorescence: bool = False,
                 infer_spikes: bool = False,
                 monitor_ensembles: bool = False) -> None:
        """
        Microscope

        :param config: The configuration with a hoisted microscope sub-configuration
        """
        self.config = config
        self.software = config.software if HAS(config) else software
        self.realtime_mode = config.realtime_mode if HAS(config) else realtime_mode
        self.motion_correction = config.motion_correction if HAS(config) else motion_correction
        self.identify_rois = config.identify_rois if HAS(config) else identify_rois
        self.extract_fluorescence = config.extract_fluorescence if HAS(config) else extract_fluorescence
        self.infer_spikes = config.infer_spikes if HAS(config) else infer_spikes
        self.monitor_ensembles = config.monitor_ensembles if HAS(config) else monitor_ensembles

        self._addr = "169.254.239.135"
        self._port = 1236
        self._timeout = 0.01
        self._client = None
        # self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._client.connect((self._addr, self._port))
        # self._client.settimeout(self._timeout)

    def __str__(self) -> str:
        return f"Microscope: {self.software}, Realtime Mode: {self.realtime_mode}"

    def build(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def destroy(self) -> None:
        pass

    def connected(self) -> bool:
        """
        Whether the microscope is connected to the python interpreter

        """
        ...

    @_format_pv_command
    def command(self, message: str) -> bool:
        self._client.sendall(message)
        response = self._client.recv(16).decode()
        response = response.split("\r\n")
        return any(("ACK" in response_ for response_ in response))

    @_format_pv_response
    def listen(self) -> str:
        return self._client.recv(4096)
