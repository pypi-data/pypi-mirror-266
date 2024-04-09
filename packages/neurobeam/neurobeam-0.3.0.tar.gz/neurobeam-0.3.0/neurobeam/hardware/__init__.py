from .camera import Camera
from .daq import DAQ
from .microscope import Microscope
from .slm import SLM
from .speaker import Speaker


# Autoregister all hardware classes
from . import camera
from . import daq
from . import microscope
from . import slm
from . import speaker


from ..registries import ComponentRegistry, auto_register

__modules__ = (camera, daq, microscope, slm, speaker)

for module_ in __modules__:
    auto_register(module_, ComponentRegistry)


# These are the things that should actually be exposed
__all__ = [
    "Camera",
    "DAQ",
    "Microscope",
    "SLM",
    "Speaker",
]
