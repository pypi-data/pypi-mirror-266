import pytest
from neurobeam.registries import (AdapterRegistry, AudioRegistry, BehaviorRegistry, CallbackRegistry, ComponentRegistry,
                                  ProviderRegistry, auto_register)
from neurobeam.exceptions import (InvalidAdapterError, InvalidComponentError, InvalidCallbackError, InvalidStateError,
                                  InvalidAudioError)


def test_adapter_registry(MockReader, MockWriter, MockTrigger, helper):
    # Test that the AdapterRegistry is registering the correct classes
    AdapterRegistry.register()(MockReader)
    assert AdapterRegistry.has("MockReader_")
    AdapterRegistry.register()(MockWriter)
    assert AdapterRegistry.has("MockWriter_")
    AdapterRegistry.register()(MockTrigger)
    assert AdapterRegistry.has("MockTrigger_")

    # Test that typecheck works
    #assert AdapterRegistry.type_check(MockReader, raise_exception=True)

    # Test that the AdapterRegistry is returning the correct classes
    assert AdapterRegistry.get("MockReader_") == MockReader
    assert AdapterRegistry.get("MockWriter_") == MockWriter
    assert AdapterRegistry.get("MockTrigger_") == MockTrigger

    # Test that the AdapterRegistry won't register random classes
    RandomClass = helper.empty_class("RandomClass")
    with pytest.raises(InvalidAdapterError):
        AdapterRegistry.type_check(RandomClass, raise_exception=True)
    AdapterRegistry.register()(RandomClass)
    assert not AdapterRegistry.has("RandomClass")

    # Test Approximate Retrieval
    assert AdapterRegistry.get("MockRead", approximate=True) == MockReader

    # Test Alias Retrieval
    assert AdapterRegistry.register(alias="MR")(MockReader)
    assert AdapterRegistry.has("MR")


def test_audio_registry(helper):

    def mock_audio(*args, **kwargs):
        return

    # Test that the AudioRegistry is registering the correct classes
    AudioRegistry.register()(mock_audio)
    assert AudioRegistry.has("mock_audio")

    # Test that typecheck works
    assert AudioRegistry.type_check(mock_audio, raise_exception=True)

    # Test that the AudioRegistry is returning the correct classes
    assert AudioRegistry.get("mock_audio") == mock_audio

    # Test that the AudioRegistry won't register random classes
    RandomClass = helper.empty_class("RandomClass")
    with pytest.raises(InvalidAudioError):
        AudioRegistry.type_check(RandomClass, raise_exception=True)
    AudioRegistry.register()(RandomClass)
    assert not AudioRegistry.has("RandomClass")

    # Test Approximate Retrieval
    assert AudioRegistry.get("mock_audi", approximate=True) == mock_audio

    # Test Alias Retrieval
    assert AudioRegistry.register(alias="MA")(mock_audio)
    assert AudioRegistry.has("MA")


def test_behavior_registry(MockState, helper):
    # Test that the BehaviorRegistry is registering the correct classes
    BehaviorRegistry.register()(MockState)
    assert BehaviorRegistry.has("MockState_")

    # Test that typecheck works
    #assert BehaviorRegistry.type_check(MockState, raise_exception=True)

    # Test that the BehaviorRegistry is returning the correct classes
    assert BehaviorRegistry.get("MockState_") == MockState

    # Test that the BehaviorRegistry won't register random classes
    RandomClass = helper.empty_class("RandomClass")
    with pytest.raises(InvalidStateError):
        BehaviorRegistry.type_check(RandomClass, raise_exception=True)
    BehaviorRegistry.register()(RandomClass)
    assert not BehaviorRegistry.has("RandomClass")

    # Test Approximate Retrieval
    assert BehaviorRegistry.get("MockSta", approximate=True) == MockState

    # Test Alias Retrieval
    assert BehaviorRegistry.register(alias="MS")(MockState)
    assert BehaviorRegistry.has("MS")


def test_callback_registry(helper):
    mock_callback = helper.mock_callback()
    true_name = mock_callback.__name__

    # Test that the CallbackRegistry is registering the correct callbacks
    CallbackRegistry.register()(mock_callback)
    assert CallbackRegistry.has(true_name)

    # Test that typecheck works
    assert CallbackRegistry.type_check(mock_callback, raise_exception=True)

    # Test that the CallbackRegistry is returning the correct callbacks
    assert CallbackRegistry.get(true_name) == mock_callback

    # Test that the CallbackRegistry won't register random classes
    RandomCallback = helper.empty_class("RandomCallback")
    with pytest.raises(InvalidCallbackError):
        CallbackRegistry.type_check(RandomCallback, raise_exception=True)
    CallbackRegistry.register()(RandomCallback)
    assert not CallbackRegistry.has("RandomCallback")

    # Test Approximate Retrieval
    assert CallbackRegistry.get(true_name[:5], approximate=True) == mock_callback

    # Test Alias Retrieval
    assert CallbackRegistry.register(alias="MC")(mock_callback)
    assert CallbackRegistry.has("MC")

    # Test collection retrieval
    assert len(CallbackRegistry.get_collection("linear_actuator")) == 3


def test_component_registry(MockComponent, helper):
    # Test that the ComponentRegistry is registering the correct classes
    ComponentRegistry.register()(MockComponent)
    assert ComponentRegistry.has("MockComponent_")

    # Test that typecheck works
    assert ComponentRegistry.type_check(MockComponent, raise_exception=True)

    # Test that the ComponentRegistry is returning the correct classes
    assert ComponentRegistry.get("MockComponent_") == MockComponent

    # Test that the ComponentRegistry won't register random classes
    RandomClass = helper.empty_class("RandomClass")
    with pytest.raises(InvalidComponentError):
        ComponentRegistry.type_check(RandomClass, raise_exception=True)
    ComponentRegistry.register()(RandomClass)
    assert not ComponentRegistry.has("RandomClass")

    # Test Approximate Retrieval
    assert ComponentRegistry.get("MockCompon", approximate=True) == MockComponent

    # Test Alias Retrieval
    assert ComponentRegistry.register(alias="MC")(MockComponent)
    assert ComponentRegistry.has("MC")


def test_provider_registry(MockComponent):
    ProviderRegistry.register(MockComponent)
    mock_component = MockComponent()
    ProviderRegistry.has("MockComponent")


def test_request_registry():
    ...


def test_auto_register():
    ...
