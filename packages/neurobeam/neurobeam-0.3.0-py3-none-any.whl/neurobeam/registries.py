from inspect import isclass, isfunction
from types import ModuleType, FunctionType
from typing import Any, Callable, Optional, Type, Union, Tuple
from weakref import WeakSet


from .extensions import (Adapter, CallbackFunction, Component, BehaviorState, ClassRegistry, InstanceRegistry,
                         check_protocol, Reader, Writer, Trigger)
from .exceptions import (DuplicateRegistrationError, MissingIdentifierError, AmbiguousCallbackInjectionError,
                         InvalidAdapterError, InvalidAudioError, InvalidCallbackError, InvalidComponentError,
                         InvalidStateError)
from .tools import EMPTY, HAS


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// STRUCTURAL TYPING & AUTO-REGISTRATION
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


def auto_register(module: ModuleType, registry: ClassRegistry) -> None:
    """
    Auto-registers all objects a certain type in a module to the specified registry. Note, you cannot use this function
    to register objects with aliases.

    :param module: The module to search for objects
    :param registry: The registry to register the objects in.
    """
    for name in dir(module):
        imported_object = getattr(module, name)
        if registry.type_check(imported_object):
            registry.register()(imported_object)


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CLASS REGISTRIES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class AdapterRegistry:
    #: dict: registry of adapter constructors
    __registry = {}

    @staticmethod
    def type_check(adapter: "Adapter", raise_exception: bool = False) -> Union[None, bool]:
        if raise_exception:
            _ = check_protocol(adapter, (Reader, Writer, Trigger), InvalidAdapterError)
            return True
        else:
            return check_protocol(adapter, (Reader, Writer, Trigger))
        # TODO: Extract me

    @classmethod
    def register(cls, alias: Optional[str] = None):  # noqa: ANN206
        """
        A decorator to register a constructor for a particular hardware device
        """
        def register_adapter(adapter):  # noqa: ANN206, ANN001, ANN201
            nonlocal alias

            alias = alias if HAS(alias) else adapter.__name__
            if cls.type_check(adapter):
                if alias in cls.__registry:
                    raise DuplicateRegistrationError(cls, alias)
                else:
                    cls.__registry[alias] = adapter
                    return adapter

        return register_adapter

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a callback is registered
        """
        return name in cls.__registry

    @classmethod
    def get(cls, name: str, approximate: bool = False) -> Callable:
        """
        Get a callback function by name

        :param name: The name of the callback function
        :param approximate: Whether to approximate the callback name if the exact name is not found
        :returns: The callback function
        :raises MissingIdentifierError: Raised if the requested callback is not in the registry.
        """
        if approximate:
            adapter = next((adapter for key, adapter in cls.__registry.items() if name in key), None)
        else:
            adapter = cls.__registry.get(name)
        if EMPTY(adapter):
            raise MissingIdentifierError(cls, name)
        return adapter


class AudioRegistry:
    #: dict: registry of audio constructors
    __registry = {}

    @staticmethod
    def type_check(audio: FunctionType, raise_exception: bool = False) -> None:
        if raise_exception:
            if not isinstance(audio, FunctionType):
                raise InvalidAudioError(audio)
            return True
        else:
            return isinstance(audio, FunctionType)

    @classmethod
    def register(cls, alias: Optional[str] = None):  # noqa: ANN206
        """
        A decorator to register a constructor for a particular hardware device
        """
        def register_audio(audio):  # noqa: ANN206, ANN001, ANN201
            nonlocal alias
            alias = alias if HAS(alias) else audio.__name__
            cls.type_check(audio)
            if alias in cls.__registry:
                raise DuplicateRegistrationError(cls, alias)
            else:
                cls.__registry[alias] = audio
                return audio

        return register_audio

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a callback is registered
        """
        return name in cls.__registry

    @classmethod
    def get(cls, name: str, approximate: bool = False) -> Callable:
        """
        Get a callback function by name

        :param name: The name of the callback function
        :param approximate: Whether to approximate the callback name if the exact name is not found
        :returns: The callback function
        :raises MissingIdentifierError: Raised if the requested callback is not in the registry.
        """
        if approximate:
            audio = next((audio for key, audio in cls.__registry.items() if name in key), None)
        else:
            audio = cls.__registry.get(name)
        if EMPTY(audio):
            raise MissingIdentifierError(cls, name)
        return audio

    @classmethod
    def __iter__(cls):
        return iter(cls.__registry.keys())


class BehaviorRegistry:
    #: dict: A dictionary of all registered behavioral state types
    __registry = {}

    @staticmethod
    def type_check(state: "State", raise_exception: bool = False) -> None:
        if check_protocol(state, BehaviorState):
            pass
        elif isfunction(state):
            if state.__name__ == "state_transition":
                pass
            else:
                if raise_exception:
                    raise InvalidStateError(state)
                else:
                    return False
        elif isclass(state):
            if state.__name__ == "Machine":
                pass
            else:
                if raise_exception:
                    raise InvalidStateError(state)
                else:
                    return False
        else:
            if raise_exception:
                raise InvalidStateError(state)
            else:
                return False
        return True
    # TODO: Extract me

    @classmethod
    def register(cls, alias: Optional[str] = None):  # noqa: ANN206
        """
        Register a state object
        """

        def register_state(state: Any) -> Any:
            nonlocal alias
            #if cls.type_check(state):
            alias = alias if HAS(alias) else state.__name__
            if alias in cls.__registry:
                raise DuplicateRegistrationError(cls, alias)
            else:
                cls.__registry[alias] = state
                return state

        return register_state

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a state is registered
        """
        return name in cls.__registry

    @classmethod
    def get(cls, name: str, approximate: bool = False) -> Any:

        if approximate:
            state = next((state for key, state in cls.__registry.items() if name in key), None)
        else:
            state = cls.__registry.get(name)
        if EMPTY(state):
            raise MissingIdentifierError(cls, name)
        return state


class CallbackRegistry:
    #: dict: A dictionary of all registered callbacks
    __registry = {}

    @staticmethod
    def type_check(callback: "CallbackFunction", raise_exception: bool = False) -> None:
        if not isinstance(callback, CallbackFunction):
            if raise_exception:
                raise InvalidCallbackError(callback)
            else:
                return False
        return True
    # TODO: Extract Me

    @classmethod
    def register(cls, alias: Optional[str] = None):  # noqa: ANN206
        """
        Register a callback function
        """
        def register_callback(callback: CallbackFunction) -> CallbackFunction:
            nonlocal alias
            alias = alias if HAS(alias) else callback.__name__
            cls.type_check(callback)
            if alias in cls.__registry:
                raise DuplicateRegistrationError(cls, alias)
            else:
                cls.__registry[alias] = callback
                return callback

        return register_callback

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a callback is registered
        """
        return name in cls.__registry

    @classmethod
    def get(cls, name: str, approximate: bool = False) -> Callable:
        """
        Get a callback function by name

        :param name: The name of the callback function
        :param approximate: Whether to approximate the callback name if the exact name is not found
        :returns: The callback function
        :raises MissingIdentifierError: Raised if the requested callback is not in the registry.
        """
        if approximate:
            callback = cls._get_matching_callbacks(name)
            if len(callback) > 1:
                raise AmbiguousCallbackInjectionError(cls, name)
            else:
                callback = callback[0]
        else:
            callback = cls.__registry.get(name)
        if EMPTY(callback):
            raise MissingIdentifierError(cls, name)
        return callback

    @classmethod
    def get_collection(cls, substring: str) -> list:
        callbacks = cls._get_matching_callbacks(substring)
        if EMPTY(callbacks):
            raise MissingIdentifierError(cls, substring)
        return callbacks

    @staticmethod
    def _get_matching_callbacks(substring: str) -> list:
        """
        Get all callback functions that contain a specific substring in their key

        :param substring: The name to search for
        :returns: A list of callback functions that contain the name
        """
        return [callback for key, callback in CallbackRegistry.__registry.items() if substring in key]


class ComponentRegistry:
    #: dict: registry of component constructors
    __registry = {}

    @staticmethod
    def type_check(component: "Component", raise_exception: bool = False) -> None:
        """
        Check if the component is a valid component.

        :param component: The component to check
        :param raise_exception: Whether to raise an exception if the component is not valid
        :raises InvalidComponentError: Raised if the component is not a valid component
        """
        if raise_exception:
            _ = check_protocol(component, Component, InvalidComponentError)
            return True
        else:
            return check_protocol(component, Component)
    # TODO: Extract me

    @classmethod
    def register(cls, alias: Optional[str] = None):  # noqa: ANN206
        """
        A decorator to register a constructor for a particular hardware device
        """

        def register_component(component):  # noqa: ANN206, ANN001, ANN201
            nonlocal alias
            alias = alias if HAS(alias) else component.__name__
            cls.type_check(component)
            if alias in cls.__registry:
                raise DuplicateRegistrationError(cls, alias)
            else:
                cls.__registry[alias] = component
                return component

        return register_component

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a callback is registered
        """
        return name in cls.__registry

    @classmethod
    def get(cls, name: str, approximate: bool = False) -> Callable:
        """
        Get a callback function by name

        :param name: The name of the callback function
        :param approximate: Whether to approximate the callback name if the exact name is not found
        :returns: The callback function
        :raises MissingIdentifierError: Raised if the requested callback is not in the registry.
        """
        if approximate:
            callback = next((component for key, component in cls.__registry.items() if name in key), None)
        else:
            callback = cls.__registry.get(name)
        if EMPTY(callback):
            raise MissingIdentifierError(cls, name)
        return callback


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// INSTANCE REGISTRIES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class ProviderRegistry:
    #: WeakSet: set of all providers
    __registry = WeakSet()

    @classmethod
    def register(cls, provider: Any):
        """
        Register a provider  object
        """
        cls.__registry.add(provider)

    @classmethod
    def has(cls, name: str, wildcard: Optional[Tuple[str, Any]] = None):
        """

        :param name:
        :param wildcard:
        :return:
        """
        if HAS(wildcard):
            key = wildcard[0]
            value = wildcard[1]
            provider = next((provider for provider in iter(cls.__registry)
                             if provider.__class__.__name__ == name
                             and getattr(provider, key, None) == value), None)
        else:
            provider = next((provider for provider in iter(cls.__registry) if provider.__class__.__name__ == name),
                            None)
        return HAS(provider)

    @classmethod
    def get(cls, name: str, wildcard: Optional[Tuple[str, Any]] = None) -> Any:
        """
        Get a provider function by name

        :param name: The name of the provider object
        :param wildcard:
        :returns: The provider object
        :raises MissingIdentifierError: Raised if the provider object is not in the registry
        """
        if HAS(wildcard):
            key = wildcard[0]
            value = wildcard[1]
            provider = next((provider for provider in iter(cls.__registry)
                             if provider.__class__.__name__ == name
                             and getattr(provider, key, None) == value), None)
        else:
            provider = next((provider for provider in iter(cls.__registry) if provider.__class__.__name__ == name),
                            None)
        if EMPTY(provider):
            raise MissingIdentifierError(cls, name)
        return provider


class RequestRegistry:
    #: WeakSet: set of all providers
    __registry = WeakSet()

    @classmethod
    def register(cls, request: Any):
        """
        Register a provider  object
        """
        cls.__registry.add(request)

    @classmethod
    def traverse(cls):
        return iter(cls.__registry)


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// INSTANCE-CACHE METACLASSES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class CachedProvider(type):
    """
    Metaclass whose subclasses' instances get added to the ProviderRegistry
    """

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        ProviderRegistry.register(instance)
        return instance


# noinspection PyPep8Naming
def Provider(meta: type = CachedProvider):
    def add_metaclass(cls):
        original_vars = cls.__dict__.copy()
        original_vars.pop("__dict__", None)
        original_vars.pop("__weakref__", None)
        return meta(cls.__name__, cls.__bases__, original_vars)
    return add_metaclass


class CachedRequest(type):
    """
    Metaclass whose subclasses' instances get added to the ProviderRegistry
    """

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        RequestRegistry.register(instance)
        return instance


# noinspection PyPep8Naming
def Request(meta: type = CachedRequest):
    def add_metaclass(cls):
        original_vars = cls.__dict__.copy()
        original_vars.pop("__dict__", None)
        original_vars.pop("__weakref__", None)
        return meta(cls.__name__, cls.__bases__, original_vars)
    return add_metaclass
