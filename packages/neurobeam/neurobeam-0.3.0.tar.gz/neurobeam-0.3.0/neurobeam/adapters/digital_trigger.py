from typing import Tuple  # Optional
from weakref import proxy

from ..configs import HoistedConfig
from ..requests import AdapterRequest
from ..registries import Provider
from ..tools import HAS


@Provider()
class DigitalTrigger:
    def __init__(self,
                 config: "HoistedConfig" = None,
                 name: str = "Digital Trigger",
                 transition_key: str = "early_ingress",
                 device_id: str = "SimDAQ",
                 digital_trigger_channel_key: str = "burrow_sensor",
                 component: "DigitalStimulus" = None,
                 ):
        self.config = config
        self.name = config.name if HAS(config) else name
        self.device_id = config.device_id if HAS(config) else device_id
        self.digital_trigger_channel_key = config.digital_trigger_channel_key if HAS(config) \
            else digital_trigger_channel_key
        self.component = proxy(component) if component else (
            AdapterRequest(self, "DigitalMultiInputStream", alias="component", wildcard=("device_id",
                                                                                         self.config.device_id)))
        self.transitions = AdapterRequest(self, "Machine", alias="transitions")
        self._running = False
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
        return self.component.channel_index.get(self.digital_trigger_channel_key)

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def command(self):
        self.transitions.get("early_ingress")()

    def initialize(self):
        ...

    def read(self):
        return self.component.data[self.channel_number, :]

    def trigger(self, time):
        data = self.read()
        if np.max(data) >= 1:
            self.command()

    def stop(self):
        self.running = False

    def __call__(self):
        self.command()
