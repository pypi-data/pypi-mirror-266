from .configs import Config
from .controller import Controller
from .factories import AdapterFactory, ComponentFactory
from .tools import HAS


"""
This function instantiates a populated neurobeam controller from the specified configuration. It should be used in the
program's main loop.
"""


def create_controller(config: "Config") -> "Controller":
    """
    Create a controller populated with adapters and components from the given configuration.

    :param config: The configuration of neurobeam used to create the controller
    :returns: The instantiated controller

    .. seealso:: :class:`Config <neurobeam.configs.Config>`\, :class:`Controller <neurobeam.controller.Controller>`
    """
    if HAS(config.components):
        components = (ComponentFactory(config).create(component) for component in range(len(config.components)))
    else:
        components = iter(())

    if HAS(config.adapters):
        adapters = (AdapterFactory(config).create(adapter) for adapter in range(len(config.adapters)))
    else:
        adapters = iter(())

    return Controller(*components, *adapters)
