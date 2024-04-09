from typing import Tuple  # Optional
from functools import partial
from weakref import proxy

import numpy as np
from psychtoolbox.audio import Slave

from ..configs import HoistedConfig
from ..hardware.speaker import Speaker
from ..factories import AudioFactory
from ..requests import AdapterRequest
from ..registries import CallbackRegistry, Provider
from ..timing import Time, Seconds
from ..tools import HAS


@Provider()
class AudioStimulus(Slave):
    # noinspection PyMissingConstructor
    def __init__(self,
                 config: "HoistedConfig",
                 name: str = "audio_stimulus",
                 style: str = "white_noise",
                 duration: Time = Seconds(1),
                 options=None,
                 stimulus: np.ndarray = None,
                 device_id: str = "Digital",
                 speaker: "Speaker" = None
                 ):
        ################################################################################################################
        # REPORTING PROGRESS
        ################################################################################################################
        self.config = config
        self.name = config.name if HAS(config) else name
        #: int: The number of times the cue has been triggered.
        self._triggers = 0
        #: int: The number of times the cue has been stopped.
        self._stops = 0
        #: np.ndarray: The stimulus to be presented.
        self._stimulus = stimulus
        self._options = config.options if HAS(config) and HAS(config.options) else {}
        self._duration = config.duration if HAS(config) else duration
        self._style = config.style if HAS(config) else style
        self.component = proxy(speaker) if HAS(speaker) else AdapterRequest(self,
                                                                            "Speaker",
                                                                            alias="component",
                                                                            wildcard=("speaker_id",
                                                                                      self.config.device_id))
        self.device_id = config.device_id if HAS(config) else device_id

        ################################################################################################################
        # INITIALIZATION
        ################################################################################################################
        #Slave.__init__(self, speaker.handle, data=stimulus, channels=speaker.channels)
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @initialized.setter
    def initialized(self, value: bool) -> None:
        if value and not self._initialized:
            factory = AudioFactory(self.component)
            self._stimulus = factory.create(self._style, **self._options)
            Slave.__init__(self, self.component.handle, data=self._stimulus, channels=self.component.channels)
            self._initialized = value

    @property
    def latency(self) -> float:
        return self.component.latency

    @property
    def running(self) -> bool:
        return self._triggers > self._stops

    @CallbackRegistry.register(alias="audio_put")
    def put(self) -> "AudioStimulus":
        self.fill_buffer(self._stimulus)

    def set_volume(self, volume: float) -> "AudioStimulus":
        self.setVolume(volume)

    @CallbackRegistry.register(alias="audio_command")
    def command(self) -> "AudioStimulus":
        self.put()
        self.write()

    @CallbackRegistry.register(alias="audio_write")
    def write(self) -> "AudioStimulus":
        self.start(1, 0, 0)
        self._triggers += 1
