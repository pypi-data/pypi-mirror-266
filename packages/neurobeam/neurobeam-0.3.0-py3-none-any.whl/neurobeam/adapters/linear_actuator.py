from typing import Union, Tuple, Optional

from memoization import cached
import numpy as np

from ..configs import HoistedConfig
from ..registries import CallbackRegistry, Provider
from ..requests import AdapterRequest
from ..timing import timer
from ..tools import HAS

from tests.conftest import report_function_call


@Provider()
class LinearActuator:
    """
    Higher-level interface for operating linear actuator

    """
    
    def __init__(self, 
                 config: Optional["HoistedConfig"] = None,
                 name: str = "LinearActuator",
                 device_id: str = "SimDAQ",
                 command_channel_key: str = "linear_actuator_command",
                 physical_range: Tuple[float, float] = (0.0, 50.0),
                 physical_units: str = "mm",
                 ):
        self.config = config
        self.name = config.name if HAS(config) else name
        self.device_id = config.device_id if HAS(config) else device_id
        self.command_channel_key = config.command_channel_key if HAS(config) else command_channel_key
        self.physical_range = config.physical_range if HAS(config) else physical_range
        self.physical_units = config.physical_units if HAS(config) else physical_units
        self.component = AdapterRequest(self,
                                        "AnalogWriter",
                                        alias="component",
                                        wildcard=("device_id", self.device_id))
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @initialized.setter
    def initialized(self, value: bool) -> None:
        if value and not self._initialized:
            self._initialized = value

    @staticmethod
    @cached(max_size=None)
    def convert_percent_to_volts(percent: np.ndarray, voltage_range: Tuple[float, float]) -> Union[float, np.ndarray]:
        return (percent / 100.0) * (voltage_range[1] - voltage_range[0]) + voltage_range[0]

    @property
    def channel_number(self) -> int:
        return self.component.channel_index.get(self.command_channel_key)

    @property
    def voltage_range(self) -> Tuple[float, float]:
        return self.component.channel_limits.get(self.command_channel_key)

    @CallbackRegistry.register(alias="linear_actuator_command")
    def command(self, value: float) -> None:
        self.put(value)
        self.write()

    @CallbackRegistry.register(alias="linear_actuator_put")
    def put(self, value: float) -> None:
        value = self.convert_percent_to_volts(value, self.voltage_range)
        self.component.data[self.channel_number, :] = value

    @CallbackRegistry.register(alias="linear_actuator_write")
    def write(self) -> None:
        self.component.write(self.component.data, auto_start=True, timeout=self.component.timeout)

    @staticmethod
    def __name__() -> str:
        return "LinearActuator"
