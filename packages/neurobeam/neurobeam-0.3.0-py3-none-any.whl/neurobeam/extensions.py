from inspect import isclass, isfunction, signature
from typing import Callable, Union, Any, Optional, Type, Tuple
from typing_extensions import Protocol, runtime_checkable
import importlib

from .configs import Config
from .timing import Time
from .tools import HAS, EMPTY


"""
Protocols & Custom Types for structural typing of various neurobeam objects during runtime type-checking and for reference 
by users to generate custom neurobeam objects. These protocols are used to define the expected methods and attributes of 
each respective neurobeam object.
"""


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MANUAL TYPE CHECKING
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


def check_protocol(cls: Any, protocol: Union[Type, Tuple[Type, ...]], exception: Optional[Callable] = None) -> bool:
    """
    Check if a class adheres to a particular protocol

    :param cls: The class to check
    :param protocol: The protocol to check against
    :param exception: The exception to raise if the check fails
    :returns: Whether the class adheres to the protocol
    """

    def check_one(cls_: Any, one_protocol: Type) -> bool:
        failed = False
        if isclass(cls):
            for attr in vars(one_protocol):
                if attr not in vars(cls) and not attr.startswith("_"):
                    failed = True
        else:
            failed = True
        if failed and HAS(exception):
            raise exception(cls)
        elif failed and EMPTY(exception):
            return False
        else:
            return True

    if isinstance(protocol, tuple):
        return any((check_one(cls, one_protocol) for one_protocol in protocol))
    else:
        return check_one(cls, protocol)
# TODO: Clean up & Debug


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CALLBACKS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class _MetaCallback(type):

    @staticmethod
    def _check_is_function(callback: Callable) -> bool:
        """
        Check if callback is a function

        :param function: The callback function to check
        :returns: Whether the callback is a function
        """
        return isfunction(callback)

    @staticmethod
    def _check_parameters(callback: Callable) -> bool:
        """
        Check if the callback has the correct parameters

        :param function: The callback function to check
        :returns: Whether the callback has the correct parameters
        """
        parameters = signature(callback).parameters
        #try:
        #    assert len(parameters) >= 1, "Callback must have at least one parameter"
        #    assert list(parameters.keys())[0] in ("self", "origin"), "First parameter must be self"
        #except AssertionError:
        #    return False
        return True

    def __instancecheck__(self, instance: Any) -> bool:
        """
        Fakes instance check so that functions with the correct parameters can be returned as instances of
        :class:`CallbackFunction <neurobeam.extensions.CallbackFunction>`

        :param instance: The instance to check
        :returns: Whether the instance is an instance of :class:`CallbackFunction <neurobeam.extensions.CallbackFunction>`

        """
        if self._check_is_function(instance) and self._check_parameters(instance):
            return isinstance(instance, object)
        else:
            super().__instancecheck__(instance)


class CallbackFunction(metaclass=_MetaCallback):
    """
    All callback functions must be of the form `def callback(origin, **kwargs) -> Any`. This class is used to define the
    Used for structural typing of callback functions. Here, we define the expected structure of a callback function
    type. Recall, that even functions are objects in python. We could just subclass function, but that would make it
    confusing for users to implement their own callbacks. Instead, we essentially use this class to fake a
    runtime-checkable protocol.
    """

    def __call__(self, *args, **kwargs):
        ...


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// COMPONENTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@runtime_checkable
class Component(Protocol):
    """
    Protocol for structural typing of neurobeam components. All neurobeam components are expected to have the included
    methods and attributes.
    """

    #: Config: Configuration object containing a sub-configuration for the component (if necessary)
    config: Config

    def build(self) -> None:
        """
        Build the component. This method should be used to initialize the component and set up any necessary resources.

        """
        ...

    def start(self) -> None:
        """
        Start the component. This method should be used to begin any necessary processes or threads that the component
        requires to function and subsequently launch the component's event loop if necessary.

        """
        ...

    def stop(self) -> None:
        """
        Stop the component. This method should be used to halt any necessary processes or threads that the component
        requires to function and subsequently close the component's event loop if necessary.

        """
        ...

    def destroy(self) -> None:
        """
        Destroy the component. This method should be used to clean up any resources that the component has acquired
        during its lifetime. This method is required, but in most cases can be left as 'pass'.

        """
        ...


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// BEHAVIOR
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@runtime_checkable
class BehaviorState(Protocol):
    """
    Protocol for structural typing of neurobeam behavior states. All neurobeam behavior states are expected to have the included
    methods and attributes.
    """
    name: str

    def state_loop(self, time: float) -> bool:
        ...

    def check_progress(self, time: float) -> float:
        ...

    def check_transition(self, time: float) -> str:
        ...

    def initialize(self) -> None:
        ...

    def transition(self) -> None:
        ...


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ADAPTERS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@runtime_checkable
class Adapter(Protocol):
    """
    Base protocol for structural typing of neurobeam adapters. That is, all neurobeam adapters are expected to have the
    following methods and attributes. Note, this is a base protocol that is not meant to directly guide user
    implementations. Instead, it is meant to be used as a base for other protocols that are more specific to the
    interface in question.
    """
    #: str: name of the interface
    name: str
    #: Config: Configuration object containing a sub-configuration for the component (if necessary)
    config: Config
    #: component request
    component: Any

    def initialized(self):
        ...


class Reader(Adapter):
    """
    Protocol for structural typing of neurobeam read adapters. All neurobeam read adapters are expected to have the
    following methods and attributes.

    """
    #: Union[Callable, CallbackRequest]: Either a request for or an implementation of a callback that will be called to
    #: read a value from the interface.
    def read(self) -> Any:
        ...


class Writer(Adapter):
    """
    Protocol for structural typing of neurobeam write adapters. All neurobeam write adapters are expected to have the
    following methods and attributes.

    """
    #: Union[Callable, CallbackRequest]: Either a request for or an implementation of a callback that will be called
    #: to write a specific value to the interface.
    #command: Union[Callable]

    def command(self, value: Any) -> None:
        ...

    #: Union[Callable, CallbackRequest]: Either a request for or an implementation of a callback that will be called to
    #: set the value written to the interface at the next write.
    def put(self, value: Any) -> None:
        ...

    #: Union[Callable, CallbackRequest]: Either a request for or an implementation of a callback that will be called
    #: to write a pre-specified value to the interface.
    def write(self, value: Any) -> None:
        ...


class Trigger(Adapter):
    """
    Protocol for structural typing of neurobeam trigger adapters. All neurobeam trigger adapters are expected to have the
    following methods and attributes.

    """
    #: Union[Callable, CallbackRequest]: Either a request for or an implementation of a callback that will be called to
    #: trigger a command callback given a specific operation on a read callback
    def command(self, value: Any) -> None:
        ...

    def read(self) -> Any:
        ...

    def trigger(self) -> None:
        ...


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DATA BUFFERS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@runtime_checkable
class DataBuffer(Protocol):
    """
    Protocol for structural typing of neurobeam data buffers. All neurobeam data buffers are expected to simultaneously write
    the data to file on each addition of data. If you are creating a data buffer that only holds the data in memory,
    then the open and close methods can simply be left as pass.
    """

    # noinspection PyPropertyDefinition
    @property
    def is_open(self) -> bool:
        """
        :Getter: Whether the associated file is open.
        :Getter Type: :class:`bool`
        :Setter: This property is read-only.
        """
        ...

    def add_data(self, data: Any) -> "DataBuffer":
        """
        Add data to the buffer. This method should be used to add data to the buffer. The data can be of any type.

        :param data: The data to be added to the buffer
        """
        ...

    def clear(self) -> "DataBuffer":
        """
        Clear the buffer. This method should be used to clear the buffer of all data.
        """
        ...

    def close(self) -> "DataBuffer":
        """
        Close the associated file for writing data.
        """
        ...

    def get_data(self) -> Any:
        """
        Get data from the buffer. This method should be used to retrieve data from the buffer.

        :returns: The data from the buffer
        """
        ...

    def open(self) -> "DataBuffer":
        """
        Open the associated file for writing data.
        """
        ...


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// REGISTRIES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@runtime_checkable
class ClassRegistry(Protocol):
    @staticmethod
    def type_check(obj: Any, raise_exception: bool = True) -> Union[None, bool]:
        ...

    @classmethod
    def register(cls, alias: Optional[str] = None) -> Callable:
        ...

    @classmethod
    def has(cls, name: str) -> bool:
        ...

    @classmethod
    def get(cls, name: str, approximate: bool = False) -> object:
        ...


@runtime_checkable
class InstanceRegistry(Protocol):
    @classmethod
    def register(cls) -> Callable:
        ...

    @classmethod
    def has(cls, name: str, wildcard: Optional[Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]]] = None) -> bool:
        ...

    @classmethod
    def get(cls, name: str, wildcard: Optional[Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]]] = None) -> object:
        ...
