from typing import Union, Tuple, Optional

import numpy as np

from ..configs import HoistedConfig
from ..registries import CallbackRegistry, Provider
from ..requests import AdapterRequest
from ..tools import HAS


@Provider()
class AnalogPulse:
    """
    Higher-level interface for operating linear actuator

    """

    def __init__(self,
                 config: Optional["HoistedConfig"] = None,
                 name: str = "AnalogPulse",
                 device_id: str = "SimDAQ",
                 analog_pulse_channel_key: str = "analog_pulse",
                 ):
        self.config = config
        self.name = config.name if HAS(config) else name
        self.device_id = config.device_id if HAS(config) else device_id
        self.analog_pulse_channel_key = config.analog_pulse_channel_key if HAS(config) else analog_pulse_channel_key
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

    @property
    def channel_number(self) -> int:
        return self.component.channel_index.get(self.analog_pulse_channel_key)

    @property
    def voltage_range(self) -> Tuple[float, float]:
        return self.component.channel_limits.get(self.analog_pulse_channel_key)

    @CallbackRegistry.register(alias="analog_pulse_command")
    def command(self, value: float) -> None:
        self.put(value)
        self.write()

    @CallbackRegistry.register(alias="analog_pulse_put")
    def put(self, value: float) -> None:
        value = self.convert_percent_to_volts(value, self.voltage_range)
        self.component.data[self.channel_number, :] = value

    @CallbackRegistry.register(alias="analog_pulse_write")
    def write(self) -> None:
        self.component.write(self.component.data, auto_start=True, timeout=self.component.timeout)

    @staticmethod
    def __name__() -> str:
        return "AnalogPulse"
