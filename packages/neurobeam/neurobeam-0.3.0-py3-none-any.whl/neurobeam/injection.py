import weakref
from functools import partial
from typing import Tuple, Any, Generator, Iterable, List
from weakref import WeakValueDictionary
import warnings
import inspect

from frozendict import frozendict

# noinspection PyProtectedMember
from .behavior.machine import Machine
from .behavior.states import State
from .exceptions import (MissingIdentifierError,
                         NoWeakRefError,
                         ItemNotAddedWarning)
from .extensions import Component, Adapter
from .hardware.daq import StreamingComponent, OnDemandComponent
from .registries import CallbackRegistry, ProviderRegistry, RequestRegistry
from .requests import AdapterRequest, CallbackRequest
from .tools import EMPTY


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DI CONTAINER
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class Container:
    """
    The Container class is a simple container for holding neurobeam components, adapters, and controllers. It is used to
    during the collection and injection of callbacks into the instances contained within it.
    """

    def __init__(self, *args):
        self.components = WeakValueDictionary()
        self.adapters = WeakValueDictionary()
        self.controller = None

        for arg in args:
            self.add_object(arg)

    def contents(self) -> Tuple[Any, ...]:
        """
        Get a tuple of the objects contained in the container

        :returns: A tuple of the objects contained in the container
        """
        return tuple(self.components.values()) + tuple(self.adapters.values()) + (self.controller(),)

    def add_object(self, obj: Any) -> None:
        """
        Add an object to the container

        :param obj: The object to add
        """
        # to resolve unavoidable circular dependency
        import neurobeam.controller
        try:
            if isinstance(obj, Component):
                self.components[id(obj)] = obj
            elif isinstance(obj, Adapter):
                self.adapters[id(obj)] = obj
            elif isinstance(obj, neurobeam.controller.Controller):
                self.controller = weakref.ref(obj)
            else:
                warnings.warn(ItemNotAddedWarning(obj), stacklevel=2)
        except TypeError:
            raise NoWeakRefError(obj)


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// INJECTION
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


def inject(*args) -> None:
    # if we only passed a controller, then extract all the components and adapters
    if len(args) == 1:
        args = (args[0], *args[0].components, *args[0].adapters)

    # collect all the neurobeam components, adapters, and controllers into a container
    container = Container(*args)

    # retrieve the cache of instantiated providers
    providers = ProviderRegistry()

    # retrieve the cache of instantiated callback requests
    requests = RequestRegistry.traverse()

    # bring in the callback registry
    callback_registry = CallbackRegistry()

    # iterate through all requests
    for request in requests:
        if isinstance(request, CallbackRequest):
            request.inject(callback_registry, providers)
        elif isinstance(request, AdapterRequest):
            request.inject(providers)
