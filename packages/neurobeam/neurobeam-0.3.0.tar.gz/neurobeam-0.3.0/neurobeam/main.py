from typing import Optional
import warnings


from .configs import Config
from .create import create_controller
from .injection import inject
from .exceptions import UISettingWarning
from .tools import HAS


def run_probe(config: Optional["Config"] = None, use_gui: bool = False) -> None:
    """
    Run the neurobeam with the given configuration.

    :param config: The configuration of neurobeam for this run.
    :param use_gui: Whether to run neurobeam with a graphical user interface.
    """
    ####################################################################################################################
    # Open the user interface if desired
    ####################################################################################################################
    if HAS(config):
        use_gui = config.use_gui if config.use_gui == use_gui else warnings.warn(UISettingWarning(config.use_gui,
                                                                                                  use_gui),
                                                                                 stacklevel=1)
    if use_gui:
        # GUI()
        pass

    ####################################################################################################################
    # Register any user customizations
    ####################################################################################################################
    # register_custom_hooks()

    ####################################################################################################################
    # Create a controller populated with adapters and components
    ####################################################################################################################
    controller = create_controller(config)

    ####################################################################################################################
    # Identify all injection requests and inject the appropriate resource/s
    ####################################################################################################################
    inject(controller)

    ####################################################################################################################
    # Start the controller as a context manager for graceful termination
    ####################################################################################################################
    with controller:
        controller.start()
