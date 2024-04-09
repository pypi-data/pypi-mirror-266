from .configs import Config, load_config
from .create import create_controller
from . import extensions

# import to perform registration
from . import adapters  # noqa: F401 // Adapter Registration
from . import behavior  # noqa: F401 // Behavior & Component Registration
from . import callbacks  # noqa: F401 // Callback Registration
from . import hardware  # noqa: F401 // Component Registration
from .tools import audio  # noqa: F401 // Audio Registration


# These are the things we want to explicitly expose to user. By using __all__ we can control what is imported when
# using the * syntax (of course), but also some IDEs will use this to provide autocompletion.
__all__ = [
    "Config",
    "create_controller",
    "extensions",
    "load_config",
]


# Confirm that user is using windows and warn them if they are using legacy windows versions
from .exceptions import LegacyWindowsWarning as _LegacyWindowsWarning
from .exceptions import OperatingSystemUnsupportedError as _OperatingSystemUnsupportedError
from platform import platform as _platform
from warnings import warn as _warn


__platform = _platform()
if "windows" not in __platform.lower():  # pragma: no cover
    raise _OperatingSystemUnsupportedError(__platform)
if not any((version in __platform for version in ["8", "10", "11"])):  # pragma: no cover
    _warn(_LegacyWindowsWarning(__platform))
