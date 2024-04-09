import warnings
from weakref import ref, proxy, WeakValueDictionary
from abc import ABC, abstractmethod
from typing import Callable, Mapping, Tuple, Any, Optional, List, Union
from types import MethodType
from .exceptions import (CallbackError, AmbiguousCallbackInjectionError, SingularCallbackCollectionError,
                         RequiredCallbackInjectionError, SingularCallbackCollectionWarning, NoOptionalCallbackWarning,
                         NoOptionalCallbackCollectionWarning, RequiredCallbackCollectionError, DispatchError,
                         CallbackKeyWarning, MissingIdentifierError)
from .extensions import CallbackFunction, Component
from .tools import EMPTY, conditional_dispatch, HAS, PatternMatching
from operator import eq
import inspect
from functools import partial, singledispatchmethod
from .registries import CallbackRegistry, Request, ProviderRegistry


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CALLBACK UTILITIES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


def bind_callback(callback: CallbackFunction, providers: ProviderRegistry,
                  wildcard: Optional[Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]]] = None) -> partial:
    """
    Bind a callback function to its instance

    :param callback: The callback function to bind
    :param providers: The providers to bind the callback to
    :param wildcard:
    :returns: The bound callback function
    """
    bound_provider = callback.__qualname__.split(".")[0]
    # TODO: This assumes there are not multiple providers with the same name. This is not necessarily true.
    provider = providers.get(bound_provider, wildcard)
    return partial(callback, proxy(provider))


def fake_callback(alias: str) -> CallbackFunction:
    return rename_callback(alias)(lambda *args, **kwargs: None)


def rename_callback(newname: str) -> Callable:
    """
    Decorator that renames a callback function

    :param newname: New callback function name
    :returns: Callback function with new name
    """

    def decorator(f: Callable) -> Callable:
        f.__name__ = newname
        return f

    return decorator


def wrap_callback_collection(collection: Tuple[Callable, ...], name: str = "callback_collection") -> Callable:
    """
    Wrap a collection of callback functions into one callback function called in the order of the input tuple

    :param collection: Tuple of callback functions
    :param name: Name of the wrapped callback function
    :returns: A new callback function that calls each callback in the collection
    """
    @rename_callback(name)
    def wrapped_callback(*args, **kwargs) -> None:  # noqa: ANN001, ANN201, ANN206
        for callback in collection:
            callback(*args, **kwargs)
    return wrapped_callback


class BoundFunction(CallbackFunction):
    """
    A class that represents a bound method
    """

    @staticmethod
    def _check_parameters(callback: Callable) -> bool:
        """
        Check if the callback has the correct parameters

        :param function: The callback function to check
        :returns: Whether the callback is a bound callback
        """
        parameters = inspect.signature(callback).parameters
        if "self" in parameters or "cls" in parameters:
            return True
        else:
            return False


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// REQUEST CONDITIONALS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


# noinspection PyPep8Naming
def IS_CALLBACK(source: CallbackFunction) -> bool:
    """
    Check if the source is a callback function or whether the function within a partial is a callback function

    :param source: The source to check
    :returns: Whether the source is a callback function
    """
    if isinstance(source, CallbackFunction):
        return True
    elif isinstance(source, partial):
        return IS_CALLBACK(source.func)
    else:
        return False


# noinspection PyPep8Naming
def IS_BOUND(source: CallbackFunction) -> bool:
    """
    Check if the source is a bound method

    :param source: The source to check
    :returns: Whether the source is a bound method
    """
    return isinstance(source, BoundFunction)


# noinspection PyPep8Naming
def IS_REGISTRY(source: CallbackRegistry) -> bool:
    """
    Check if the source is a callback registry

    :param source: The source to check
    :returns: Whether the source is a callback registry
    """
    return isinstance(source, CallbackRegistry)


# noinspection PyPep8Naming
def IS_APPROXIMATE(self: "CallbackRequest") -> bool:
    """
    Check if the callback request is approximate

    :param self: The callback request
    :returns: Whether the callback request is approximate
    """
    return self.approximate


# noinspection PyPep8Naming
def IS_REQUIRED(self: "CallbackRequest") -> bool:
    """
    Check if the callback request is required

    :param self: The callback request
    :returns: Whether the callback request is required
    """
    return self.required


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CALLBACK REQUESTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class _SingleInjection:
    def __init__(self,
                 requesting_instance: Any,
                 key: str,
                 alias: Optional[str] = None,
                 approximate: bool = False,
                 required: bool = False,
                 arguments: Optional[dict[str, Any]] = None,
                 wildcard: Optional[Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]]] = None):
        self.requesting_instance = requesting_instance
        self.key = key
        self.alias = alias if HAS(alias) else key
        self.approximate = approximate
        self.required = required
        self.arguments = arguments if HAS(arguments) else {}
        self.wildcard = wildcard

    @conditional_dispatch
    def inject(self,
               source: Union[CallbackFunction, CallbackRegistry, None],
               providers: Optional[dict] = None) -> None:
        raise DispatchError(self.requesting_instance.__class__.__name__)

    @inject.register(lambda self, source, providers=None: IS_CALLBACK(source))
    def _inject_callback(self, source: CallbackFunction, providers: Optional[dict] = None) -> None:
        if IS_BOUND(source):
            source = bind_callback(source, providers, self.wildcard)
        if HAS(self.arguments):
            source = partial(source, **self.arguments)
        setattr(self.requesting_instance, self.alias, source)

    @inject.register(lambda self, source, providers=None: IS_REGISTRY(source))
    def _inject_registry(self, source: CallbackRegistry, providers: Optional[dict] = None) -> None:
        try:
            callback = source.get(self.key, approximate=self.approximate)
        except MissingIdentifierError:
            if self.required:
                raise RequiredCallbackInjectionError(self.requesting_instance.__class__.__name__, self.alias)
            else:
                warnings.warn(NoOptionalCallbackWarning(self.requesting_instance.__class__.__name__, self.alias),
                              stacklevel=3)
                callback = fake_callback(self.alias)
        finally:
            # noinspection PyUnboundLocalVariable
            self.inject(callback, providers)

    @inject.register(lambda self, source, providers=None: EMPTY(source))
    def _inject_empty(self, source: None, providers: Optional[dict] = None) -> None:
        if self.required:
            raise RequiredCallbackInjectionError(self.requesting_instance.__class__.__name__, self.alias)
        else:
            warnings.warn(NoOptionalCallbackWarning(self.requesting_instance.__class__.__name__, self.alias),
                          stacklevel=3)
            callback = fake_callback(self.alias)
            self.inject(callback, providers)


class _CollectionInjection:
    def __init__(self,
                 requesting_instance: Any,
                 key: str,
                 alias: str,
                 approximate: bool = False,
                 required: bool = False,
                 arguments: Optional[dict[str, Any]] = None,
                 wildcard: Optional[Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]]] = None):
        self.requesting_instance = requesting_instance
        self.key = None
        self.alias = None
        self.approximate = None
        self.required = required
        self.wildcard = wildcard

        # parse keys
        if isinstance(key, tuple):
            self.key = key
            self.approximate = False
            if HAS(arguments) and (len(key) != len(arguments)):
                raise AssertionError("The number of keys and arguments must be equal")
                # TODO: Make a custom exception
            if EMPTY(alias):
                raise AssertionError("An alias must be provided for a collection of callbacks")
                # TODO: Make a custom exception
            self.alias = alias
            self.arguments = arguments
        else:
            self.key = key
            self.alias = alias if HAS(alias) else key
            self.approximate = True
            if HAS(self.arguments):
                warnings.warn("beep", stacklevel=3)
                # TODO: Make a custom warning
            self.arguments = None
        self.required = required

    @conditional_dispatch
    def inject(self,
               source: Union[Tuple[CallbackFunction, ...], CallbackRegistry, None],
               providers: Optional[dict] = None) -> None:
        raise DispatchError(self.requesting_instance.__class__.__name__)

    @inject.register(lambda self, source, providers=None: all(map(IS_CALLBACK, source)))
    def _inject_callback(self, source: CallbackFunction, providers: Optional[dict] = None) -> None:
        callbacks = []
        for idx, callback in enumerate(source):
            if IS_BOUND(source):
                callback = bind_callback(source, providers, self.wildcard)
            if HAS(self.arguments):
                callback = partial(source, **self.arguments[idx])
            callbacks.append(callback)
        wrapped_callback = wrap_callback_collection(tuple(callbacks), self.alias)
        setattr(self.requesting_instance, self.alias, wrapped_callback)

    # noinspection PyUnboundLocalVariable
    @inject.register(lambda self, source, providers=None: IS_REGISTRY(source) and IS_APPROXIMATE(self))
    def _inject_registry_approximate(self, source: CallbackRegistry, providers: Optional[dict] = None) -> None:
        try:
            callbacks = source.get_collection(self.key)
        except MissingIdentifierError:
            callbacks = []
        finally:
            if len(callbacks) <= 1 and self.required:
                raise RequiredCallbackCollectionError(self.requesting_instance.__class__.__name__, self.alias)
            elif len(callbacks) == 0 and not self.required:
                callbacks = [fake_callback(self.alias), fake_callback(self.alias)]
            elif len(callbacks == 1) and not self.required:
                warnings.warn(SingularCallbackCollectionWarning(self.requesting_instance.__class__.__name__,
                                                                self.alias),
                              stacklevel=3)
                callbacks = [callbacks[0], fake_callback(self.alias)]
            self.inject(callbacks, providers)

    @inject.register(lambda self, source, providers=None: IS_REGISTRY(source) and not IS_APPROXIMATE(self))
    def _inject_registry(self, source: CallbackRegistry, providers: Optional[dict] = None) -> None:
        callbacks = []
        for callback in self.key:
            try:
                callbacks = source.get(self.key, approximate=False)
            except MissingIdentifierError:
                if self.required:
                    raise RequiredCallbackCollectionError(self.requesting_instance.__class__.__name__, self.alias)
        if len(callbacks) <= 1 and self.required:
            raise RequiredCallbackCollectionError(self.requesting_instance.__class__.__name__, self.alias)
        elif len(callbacks) == 0 and not self.required:
            callbacks = [fake_callback(self.alias), fake_callback(self.alias)]
        elif len(callbacks == 1) and not self.required:
            warnings.warn(SingularCallbackCollectionWarning(self.requesting_instance.__class__.__name__, self.alias),
                          stacklevel=3)
            callbacks = [callbacks[0], fake_callback(self.alias)]
        self.inject(callbacks, providers)

    @inject.register(lambda self, source, providers=None: EMPTY(source))
    def _inject_empty(self, source: None, providers: Optional[dict] = None) -> None:
        if self.required:
            raise RequiredCallbackInjectionError(self.requesting_instance.__class__.__name__, self.alias)
        else:
            warnings.warn(NoOptionalCallbackWarning(self.requesting_instance.__class__.__name__, self.alias),
                          stacklevel=3)
            callbacks = [fake_callback(self.alias), fake_callback(self.alias)]
            self.inject(callback, providers)


@Request()
class CallbackRequest:
    def __init__(self,
                 requesting_instance: Any,
                 key: Union[str, Tuple[str, ...]],
                 alias: Optional[str] = None,
                 approximate: bool = False,
                 collection: bool = False,
                 required: bool = False,
                 arguments: Optional[Union[dict[str, Any], Tuple[dict[str, Any], ...]]] = None,
                 wildcard: Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]] = None):
        ##############################################################################################################
        # INSTANTIATE IMPLEMENTATION
        ################################################################################################################
        collection_ = True if collection or isinstance(key, tuple) else False
        if collection_:
            self._implementation = _CollectionInjection(requesting_instance,
                                                        key,
                                                        alias,
                                                        approximate,
                                                        required,
                                                        arguments,
                                                        wildcard)
        else:
            self._implementation = _SingleInjection(requesting_instance,
                                                    key,
                                                    alias,
                                                    approximate,
                                                    required,
                                                    arguments,
                                                    wildcard)

            ############################################################################################################
            # ENSURE ALIAS RESERVED
            ############################################################################################################
            setattr(self._implementation.requesting_instance, self._implementation.alias, None)

    def __str__(self) -> str:
        return f"Request to inject callback {self.alias} into {self.requesting_instance.__class__.__name__}"

    @property
    def alias(self) -> str:
        return self._implementation.alias

    @property
    def approximate(self) -> bool:
        return self._implementation.approximate

    @property
    def collection(self) -> bool:
        return True if isinstance(self._implementation, _CollectionInjection) else False

    @property
    def key(self) -> Union[str, Tuple[str, ...]]:
        return self._implementation.key

    @property
    def requesting_instance(self) -> Any:
        return self._implementation.requesting_instance

    @property
    def required(self) -> bool:
        return self._implementation.required

    def warn_if_alias_unreserved(self) -> None:
        if not hasattr(self._implementation.requesting_instance, self._implementation.alias):
            warnings.warn(CallbackKeyWarning(self._implementation.requesting_instance.__class__.__name__,
                                             self._implementation.alias),
                          stacklevel=2)

    def inject(self,
               source: Union[CallbackFunction, Tuple[CallbackFunction, ...], CallbackRegistry, None],
               providers: Optional[ProviderRegistry] = None) -> None:
        self._implementation.inject(source, providers)

    def __call__(self, *args, **kwargs):
        raise CallbackError(self.requesting_instance.__class__.__name__, self.alias)


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ADAPTER REQUESTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@Request()
class AdapterRequest:
    def __init__(self,
                 requesting_instance: Any,
                 key: str,
                 alias: Optional[str] = None,
                 wildcard: Optional[Tuple[str, Any]] = None):
        self.requesting_instance = requesting_instance
        self.key = key
        self.alias = alias if HAS(alias) else key
        self.wildcard = wildcard

    def __str__(self) -> str:
        return f"Request to inject {self.key} instance into {self.requesting_instance.__class__.__name__}"

    def inject(self, providers: ProviderRegistry) -> None:
        provider = providers.get(self.key, self.wildcard)
        setattr(self.requesting_instance, self.alias, provider)
        setattr(self.requesting_instance, "initialized", True)


@Request()
class TriggerRequest:
    def __init__(self,
                 key: str,
                 wildcard: Optional[Tuple[str, Any]] = None):
        self.key = key
        self.wildcard = wildcard

    def __str__(self) -> str:
        return f"Request to inject {self.key} instance into {self.requesting_instance.__class__.__name__}"

    def inject(self, providers: ProviderRegistry) -> None:
        return providers.get(self.key, self.wildcard)
