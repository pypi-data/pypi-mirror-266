from . import console
from . import debug

__modules__ = (console, debug)


# Register all callbacks automatically
from ..registries import auto_register as _auto_register, CallbackRegistry
from ..extensions import CallbackFunction


for module_ in __modules__:
    _auto_register(module_, CallbackRegistry)
