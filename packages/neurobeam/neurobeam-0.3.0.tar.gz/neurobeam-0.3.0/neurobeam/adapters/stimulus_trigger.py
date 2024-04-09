from typing import Tuple  # Optional
from weakref import proxy

from sys import float_info

MAX = float_info.max


from ..configs import HoistedConfig
from ..requests import AdapterRequest
from ..registries import Provider, CallbackRegistry
from ..tools import HAS


@Provider()
class StimulusTrigger:
    def __init__(self,
                 config: "HoistedConfig" = None,
                 name: str = "Stimulus Trigger",
                 component=None,
                 relative_onset: float = 10000.0,
                 ):
        self.config = config
        self.name = config.name if HAS(config) else name
        self.component = component = proxy(component) if component else (
            AdapterRequest(self,
                           "AudioStimulus",
                           alias="component",
                           wildcard=("name", self.config.stimulus_name)))
        self.relative_onset = config.relative_onset if HAS(config) else relative_onset
        self._running = False
        self.onset = MAX
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @initialized.setter
    def initialized(self, value: bool) -> None:
        if value and not self._initialized:
            self._initialized = value

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def command(self):
        self.component.write()

    def read(self):
        return self.running

    @CallbackRegistry.register(alias="stimulus_trigger_trigger")
    def trigger(self, time):
        if self.read() and time >= self.onset:
            self.command()
            self.running = True

    def stop(self):
        self.running = False

    @CallbackRegistry.register(alias="stimulus_trigger_initialize")
    def initialize(self, start_time):
        self.onset = start_time - self.component.component.latency + self.relative_onset
        self.component.put()

    def __call__(self):
        print(f"Triggering stimulus: {self.name}")
        self.command()
