from .linear_actuator import LinearActuator
from .analog_pulse import AnalogPulse
from .audio_stimulus import AudioStimulus
from .stimulus_trigger import StimulusTrigger
from .digital_trigger import DigitalTrigger
from typing import Any

# auto-register all the classes in these modules
from ..registries import auto_register as _auto_register
from ..registries import AdapterRegistry
from . import linear_actuator
from . import analog_pulse
from . import audio_stimulus
from . import digital_trigger
from . import stimulus_trigger


__modules__ = (linear_actuator, analog_pulse, audio_stimulus, stimulus_trigger, digital_trigger)

for module_ in __modules__:
    _auto_register(module_, AdapterRegistry)

# Exposure
__all__ = [
    "AudioStimulus"
    "AnalogPulse",
    "DigitalTrigger",
    "LinearActuator",
    "StimulusTrigger",
]
