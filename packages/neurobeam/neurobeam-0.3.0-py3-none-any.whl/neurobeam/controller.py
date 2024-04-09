from typing import Union, Any
import warnings

from .exceptions import (InvalidAdapterWarning, InvalidComponentWarning, SingletonError, EmptyControllerWarning,
                         EmptyControllerError, ControllerImmutabilityWarning)
from .extensions import Component, Adapter, Reader, Writer, Trigger
from .tools import HAS, EMPTY
from .registries import CallbackRegistry, Provider


@Provider()
class Controller:
    """
    Controller class for neurobeam. The controller is a singleton object that references all the components necessary for
    the neurobeam to function. The controller is responsible for starting, stopping, and destroying the components within
    the controller. The instance of the controller is held in a weak reference as a name-mangled class attribute to
    ensure that only one instance of the controller class is ever active. This singleton-ness was implemented to
    ensure users only ever run one experiment per interpreter and not due to some specific implementation requirement.

    """
    #: Union[Tuple[Component, ...], List[Component]]: List of components within the controller; tuple when controller
    # is locked
    components = []

    #: Union[Tuple[Adapter, ...], List[Adapter]]: List of adapters within the controller; tuple when controller
    # is locked
    adapters = []

    #: bool: Whether the controller is running
    _running = False

    def __init__(self, *args) -> None:
        ################################################################################################################
        # REFERENCE COMPONENTS & adapterS
        ################################################################################################################
        if len(args) == 0:
            warnings.warn(EmptyControllerWarning(), stacklevel=2)
        for arg in args:
            if isinstance(arg, Component):
                self.add_component(arg)
            elif isinstance(arg, (Adapter, Reader, Writer, Trigger)):
                self.add_adapter(arg)
            else:  # If invalid, just raise a warning for both
                warnings.warn(InvalidComponentWarning(arg), stacklevel=2)
                warnings.warn(InvalidAdapterWarning(arg), stacklevel=2)

    def __str__(self) -> str:
        return (f"Controller containing the following components and adapters: "
                f"{[thing.__name__() for thing in self.components + self.adapters]}")

    @property
    def running(self) -> bool:
        """
        :Getter: Returns whether the controller is running.
        :Getter Type: :class:`bool`
        :Setter: This property is read-only
        :Setter Type: :class:`bool`
        """
        return self._running

    @staticmethod
    def __name__() -> str:
        return "Controller"

    @running.setter
    def running(self, value: bool) -> None:
        if value == self._running:
            pass
        elif value:
            # convert to tuple for faster access and immutability
            self.components = tuple(self.components)
            self.adapters = tuple(self.adapters)
            self._running = True
        else:
            # convert to list to allow mutability
            self.components = list(self.components)
            self.adapters = list(self.adapters)
            self._running = False

    @CallbackRegistry.register(alias="controller_add_component")
    def add_component(self, component: Component) -> None:
        """
        Adds a component to the controller.

        :param component: A component to add to the controller
        :raises InvalidComponentWarning: Raised if the component is not a valid component
        :raises ControllerImmutabilityWarning: Raised if the controller is running
        """
        if not isinstance(component, Component):
            warnings.warn(InvalidComponentWarning(component), stacklevel=2)
        elif self.running:
            warnings.warn(ControllerImmutabilityWarning(), stacklevel=2)
        else:
            self.components.append(component)

    @CallbackRegistry.register(alias="controller_add_adapter")
    def add_adapter(self, adapter: Union[Reader, Writer, Trigger]) -> None:
        """
        Adds an adapter to the controller.

        :param adapter: An adapter to add to the controller
        :raises InvalidAdapterWarning: Raised if the adapter is not a valid adapter
        :raises ControllerImmutabilityWarning: Raised if the controller is running
        """
        if not isinstance(adapter, (Adapter, Reader, Writer, Trigger)):
            warnings.warn(InvalidAdapterWarning(adapter), stacklevel=2)
        elif self.running:
            warnings.warn(ControllerImmutabilityWarning(), stacklevel=2)
        else:
            self.adapters.append(adapter)

    @CallbackRegistry.register()
    def start(self) -> None:
        """
        Start the controller. This method should be used to begin any necessary processes or threads that the
        components within the controller require to function.

        """
        if not self.running:
            # noinspection PyCallingNonCallable
            self.running = True
            if EMPTY(self.components + self.adapters):
                raise EmptyControllerError()
            for component in self.components:
                print(f"{component} is starting...\r\r")
                component.start()
                print(f"{component} is starting...success.")

    @CallbackRegistry.register()
    def stop(self) -> None:
        """
        Stop the controller. This method should be used to halt any necessary processes or threads that the
        components within the controller require to function.

        """
        if self.running:
            self.running = False
            if EMPTY(self.components + self.adapters):
                raise EmptyControllerError()
            for component in self.components:
                print(f"{component} is stopping...\r\r")
                component.stop()
                print(f"{component} is stopping...success.")

    @CallbackRegistry.register()
    def destroy(self) -> None:
        """
        Destroy the controller. This method should be used to destroy any necessary processes, threads, or other
        resources that the components within the controller require to function.

        """
        if self.running:
            self.stop()
        if EMPTY(self.components + self.adapters):
            raise EmptyControllerError()
        print("Destroying adapters...\r\r")
        self.adapters = []
        print("Destroying adapters...success.")
        for component in self.components:
            print(f"{component} is destroying...\r\r")
            component.destroy()
            print(f"{component} is destroying...success.")
        self.clear()

    @CallbackRegistry.register()
    def clear(self) -> None:
        if self.running:
            self.destroy()

        self.components = []
        self.adapters = []

    def __del__(self):
        if self.running:
            self.destroy()

    def __enter__(self) -> "Controller":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()
        self.destroy()
