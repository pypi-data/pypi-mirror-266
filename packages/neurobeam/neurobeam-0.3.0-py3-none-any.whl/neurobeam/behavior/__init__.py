from .behavior import Behavior


# Autoregistration
from ..extensions import BehaviorState
from ..registries import auto_register, BehaviorRegistry
from . import states
from . import machine
from . import transitions

__modules__ = (machine, transitions)

#for module_ in __modules__:
#    auto_register(module_, BehaviorRegistry)

# Exposure
__all__ = [
    "Behavior",
]
