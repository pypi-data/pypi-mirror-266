import pytest

from neurobeam.extensions import CallbackFunction
from neurobeam.requests import bind_callback, fake_callback, rename_callback, wrap_callback_collection, BoundFunction
from neurobeam.requests import _SingleInjection, _CollectionInjection, CallbackRequest, AdapterRequest


def test_bind_callback():
    ...


def test_fake_callback():
    function = fake_callback("faker")
    assert function.__name__ == "faker"
    assert function() is None
    assert isinstance(function, CallbackFunction)


def test_rename_callback():
    function = fake_callback("faker")
    assert function.__name__ == "faker"
    function = rename_callback("renamed")(function)
    assert function.__name__ == "renamed"
    assert function() is None
    assert isinstance(function, CallbackFunction)


def test_wrap_callback_collection():
    function0 = fake_callback("faker0")
    function1 = fake_callback("faker1")
    function2 = fake_callback("faker2")

    wrapped_function = wrap_callback_collection((function0, function1, function2), name="wrapped_function")
    assert wrapped_function.__name__ == "wrapped_function"
    assert wrapped_function() is None
    assert isinstance(wrapped_function, CallbackFunction)


def test_bound_function():
    ...


def test_implementation_selection(MockComponent):
    mc = MockComponent()

    setattr(mc, "mock_single_callback_request", None)
    mc.mock_single_callback_request = CallbackRequest(mc,
                                                      key="reporting_console_start",
                                                      alias="mock_single_callback_request")
    setattr(mc, "mock_collection_callback_request", None)
    mc.mock_collection_callback_request = CallbackRequest(mc,
                                                          ("reporting_console_start", "reporting_console_stop"),
                                                          alias="mock_collection_callback_request")

    assert isinstance(mc.mock_single_callback_request._implementation, _SingleInjection)
    assert isinstance(mc.mock_collection_callback_request._implementation, _CollectionInjection)
