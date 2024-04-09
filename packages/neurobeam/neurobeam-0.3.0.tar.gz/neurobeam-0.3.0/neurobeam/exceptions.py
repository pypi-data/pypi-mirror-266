from typing import Any
from .static import SUPPORTED_MICROSCOPES


# TODO: Prune unused exceptions
"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// General Errors & Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class UISettingWarning(UserWarning):
    """
    Raised when the configuration and command line arguments for the user interface are inconsistent
    """
    def __init__(self, config_setting: bool, command_setting: bool):
        self.config_setting = config_setting
        self.command_setting = command_setting
        super().__init__(f"The config setting for the user interface is {self.config_setting} while the command line"
                         f"setting is {self.command_setting}. Using the command line setting...")


class OperatingSystemUnsupportedError(OSError):
    """
    Raised when the operating system is not supported
    """
    def __init__(self, os_name: str):
        self.os_name = os_name
        super().__init__(f"Probe is only supported on Windows operating systems. Detected {self.os_name}")


class NotPermittedTypeError(TypeError):
    """
    Raised when a type is not permitted
    """
    def __init__(self, key: str, pos: int, permitted: Any):
        self.key = key
        self.pos = pos
        self.permitted = permitted
        super().__init__(f"Argument {self.key} at position {self.pos} must be of type {self.permitted}")


class SingletonError(RuntimeError):
    """
    Raised when attempting to create a second instance of a singleton
    """

    def __init__(self, singleton: object):
        self.singleton = singleton
        self.name = self.singleton.__name__ if hasattr(self.singleton, "__name__") \
            else type(self.singleton).__name__
        super().__init__(f"{self.name} is a singleton and cannot be instantiated more than once")


class NoWeakRefError(RuntimeError):
    """
    Raised when an object is not able to be weakly referenced
    """
    def __init__(self, obj: object):
        self.obj = obj
        super().__init__(f"Object {self.obj} cannot be weakly referenced")


class DispatchError(RuntimeError):
    """
    Raised when a dispatch method fails
    """
    def __init__(self, obj: object):
        self.obj = obj
        super().__init__(f"Dispatch failed for object {self.obj}")


class ImmutableInstanceWarning(RuntimeWarning):
    """
    Raised when attempting to set an attribute on an immutable instance
    """
    def __init__(self, instance: object):
        self.instance = instance
        super().__init__(f"{self.instance.__class__.__name__} is immutable and cannot be modified")


class LegacyWindowsWarning(UserWarning):
    """
    Raised when using legacy windows
    """
    def __init__(self, os_name: str):
        self.os_name = os_name
        super().__init__(f"Using legacy Windows operating system {self.os_name}."
                         f"Probe's performance may be affected. See 'timer' documentation"
                         f"for details.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Configuration Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class UpdateVersionWarning(UserWarning):
    """
    Raised when the configuration version should be updated
    """
    def __init__(self, version: str, expected: str):
        self.version = version
        self.expected = expected
        super().__init__(f"It is advised to update neurobeam to the latest version at your earliest convenience!"
                         f"Configuration version {self.version} does not match the expected version {self.expected}")


class VersionForwardCompatibilityWarning(UserWarning):
    """
    Raised when the configuration version does not match the expected version (forward compatibility of major versions)
    """
    def __init__(self, version: str, expected: str):
        self.version = version
        self.expected = expected
        super().__init__(f"Forward Compatibility of major versions is not guaranteed! "
                         f"Configuration version {self.version} does not match the expected version {self.expected}")


class VersionBackwardCompatibilityWarning(UserWarning):
    """
    Raised when the configuration version does not match the expected version (backward compatibility of minor versions)
    """

    def __init__(self, version: str, expected: str):
        self.version = version
        self.expected = expected
        super().__init__(f"Backwards compatibility of minor versions is not guaranteed!"
                         f"Configuration version {self.version} does not match the expected version {self.expected}")


class ValidationFailureWarning(UserWarning):
    """
    Raised when a configuration update fails due to the value set not matching validation requirements
    """
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        super().__init__(f"Failed to update configuration key {self.key} with value {self.value}")


class ConfigurationFallbackWarning(RuntimeWarning):
    """
    Raised when falling-back to existing configuration
    """
    def __init__(self):
        super().__init__("Invalid configuration. Falling-back to existing configuration.")


class NoConfigurationWarning(RuntimeWarning):
    """
    Raised when trying to set a sub-configuration when no base configuration
    is available
    """

    def __init__(self, sub_configuration: object):
        self.sub_configuration = sub_configuration
        self.name = sub_configuration.__name__ if hasattr(sub_configuration, "__name__") \
            else type(sub_configuration).__name__
        super().__init__(f"Cannot set {self.name} without a base configuration")


class HeadlessWarning(UserWarning):
    """
    Raised when the user interface is headless
    """
    def __init__(self):
        super().__init__("Running in headless mode. No user interface will be displayed.")


class DualUserInterfaceError(AssertionError):
    """
    Raised when attempting to use both GUI and Console User Interfaces
    """
    def __init__(self):
        super().__init__("Cannot use both GUI and Console User Interfaces")


class VersionBackwardCompatibilityError(ValueError):
    """
    Raised when the configuration version does not match the expected version
    """
    def __init__(self, version: str, expected: str):
        self.version = version
        self.expected = expected
        super().__init__(f"Probe does not support backwards compatibility of major versions! Configuration version "
                         f"{self.version} does not match the expected version {self.expected}")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Factory or Registry Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class DuplicateRegistrationError(RuntimeError):
    """
    Raised when the factory fails to register a class due to duplicate keys
    """
    def __init__(self, factory: object, class_to_register: object):
        self.factory = factory
        self.class_to_register = class_to_register
        super().__init__(f"Factory {self.factory.__class__.__name__} failed to register {self.class_to_register} "
                         f"due to a previously registered constructor with an identical key")


class MissingIdentifierError(KeyError):
    """
    Raised when an identifier is missing
    """
    def __init__(self, factory: object, identifier: str):
        self.factory = factory
        self.identifier = identifier
        super().__init__(f"Identifier {self.identifier} is missing in {self.factory.__class__.__name__}")


class InvalidComponentError(AttributeError):
    """
    Raised when an invalid component is registered
    """
    def __init__(self, component: object):
        self.component = component
        super().__init__(f"Component {self.component} is not a valid neurobeam component.")


class InvalidAdapterError(AttributeError):
    """
    Raised when an invalid adapter is registered
    """
    def __init__(self, adapter: object):
        self.adapter = adapter
        super().__init__(f"Adapter {self.adapter} is not a valid neurobeam adapter.")


class InvalidAudioError(AttributeError):
    """
    Raised when an invalid audio is registered
    """
    def __init__(self, audio: object):
        self.audio = audio
        super().__init__(f"Audio {self.audio} is not a valid neurobeam audio.")


class InvalidCallbackError(AttributeError):
    """
    Raised when an invalid callback is registered
    """
    def __init__(self, callback: object):
        self.callback = callback
        super().__init__(f"Callback {self.callback} is not a valid neurobeam callback.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Controller Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class ControllerImmutabilityWarning(RuntimeWarning):
    """
    Raised when attempting to modify the controller when running & immutable
    """
    def __init__(self):
        super().__init__("Controller is running and immutable. Cannot modify components or adapters.")


class EmptyControllerWarning(RuntimeWarning):
    """
    Raised when the controller is empty
    """
    def __init__(self):
        super().__init__("Controller is empty. Please add components and adapters.")


class EmptyControllerError(RuntimeError):
    """
    Raised when the controller is empty
    """
    def __init__(self):
        super().__init__("Controller is empty. Cannot execute control methods without components and "
                         "adapters to control.")


class InvalidComponentWarning(RuntimeWarning):
    """
    Raised when an invalid object is passed to the controller as a positional argument or through the
    :method:`Controller.add_component <neurobeam.controllers.Controller.add_component>` method
    """
    def __init__(self, component: Any):
        self.component = component
        super().__init__(f"Component {self.component} is not a valid neurobeam component.")


class InvalidAdapterWarning(RuntimeWarning):
    """
    Raised when an invalid adapter is passed to the controller as a positional argument or through the
    :method:`Controller.add_adapter <neurobeam.controllers.Controller.add_adapter>` method
    """
    def __init__(self, adapter: Any):
        self.adapter = adapter
        super().__init__(f"Adapter {self.adapter} is not a valid neurobeam adapter.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Filesystems / Data Buffers Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class DataReorganizationWarning(RuntimeWarning):
    """
    Raised when data reorganization was unsuccessful
    """
    def __init__(self, elements: int, shape: tuple):
        self.elements = elements
        self.shape = shape
        super().__init__(f"The number of elements {self.elements} in the written data cannot be coerced to the "
                         f"requested shape {self.shape}")


class DesynchronizedBuffersWarning(RuntimeWarning):
    """
    Raised when a group of buffers is desynchronized
    """
    def __init__(self, buffers: tuple):
        self.buffers = buffers
        super().__init__(f"The following buffers are desynchronized: {self.buffers}")


class EmptyEventLogWarning(RuntimeWarning):
    """
    Raised when argument to the event log is empty
    """
    def __init__(self):
        super().__init__("Event log was not supplied any argument")


class InvalidExtensionWarning(UserWarning):
    """
    Raised when an invalid file extension is used
    """
    def __init__(self, key: str, pos: int, extension: str, permitted: Any):
        self.key = key
        self.pos = pos
        self.extension = extension
        self.permitted = permitted
        super().__init__(f"Argument {self.key} at position {self.pos} has invalid file extension {self.extension}. "
                         f"Expected extension {self.permitted} and coerced to {self.permitted}.")


class OverloadedEventLogWarning(RuntimeWarning):
    """
    Raised when the event log is overloaded
    """
    def __init__(self, args: Any):
        self.args = args
        super().__init__(f"Event log was overloaded with {len(self.args)} arguments: {self.args}")


class PathMismatchWarning(RuntimeWarning):
    """
    Raised the eventlog is successfully called from the instance registry but a path is provided that does not match
    the path located in the instance registry.
    """
    def __init__(self, key: str, path: str, expected: str):
        self.key = key
        self.path = path
        self.expected = expected
        super().__init__(f"The passed instance registry key {self.key} has path {self.expected} that does not match the"
                         f"passed path {self.path}")


class RingSizeMismatchWarning(RuntimeWarning):
    """
    Raised the eventlog is successfully called from the instance registry but a ring size is provided that does not
    match the ring size specified by the existing instance.
    """

    def __init__(self, key: str, ring_size: int, expected: int):
        self.key = key
        self.ring_size = ring_size
        self.expected = expected
        super().__init__(
            f"The passed instance registry key {self.key} has ring size {self.expected} that does not match the"
            f"passed ring size {self.ring_size}")


class InvalidFilenameError(ValueError):
    """
    Raised when an invalid filename is used
    """
    def __init__(self, key: str, pos: int, filename: str):
        self.key = key
        self.filename = filename
        self.pos = pos
        super().__init__(f"Argument {self.key} at position {self.pos} has invalid filename {self.filename}."
                         f"Please use only alphanumeric characters and underscores.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Callback Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class CallbackError(RuntimeError):
    """
    Raised when a component calls a callback that has not been injected

    """
    def __init__(self, obj: str, callback: str):
        self.obj = obj
        self.callback = callback
        super().__init__(f"Component {self.obj} called {self.callback}, but it was not injected!")


class AmbiguousCallbackInjectionError(RuntimeError):
    """
    Raised when the injector fails to inject an approximate callback into a component due to multiple callbacks
    matching the search tag.

    """
    def __init__(self, obj: str, callback: str):
        self.obj = obj
        self.callback = callback
        super().__init__(f"Callback with tag {self.callback} is ambiguous for {self.obj}; multiple callbacks "
                         f"match the search tag.")


class SingularCallbackCollectionError(RuntimeError):
    """
    Raised when the injector is able to locate only one callback within a required callback collection request.
    """
    def __init__(self, obj: str, callback: str):
        self.obj = obj
        self.callback = callback
        super().__init__(f"Component {self.obj} requested a required callback collection with tag "
                         f"{self.callback} but only one callback was located.")


class RequiredCallbackCollectionError(RuntimeError):
    """
    Raised when the injector fails to inject a required callback collection into a component
    """
    def __init__(self, obj: str, callback: str):
        self.obj = obj
        self.callback = callback
        super().__init__(f"Failed to inject required callback collection {self.callback} into {self.obj}")


class RequiredCallbackInjectionError(RuntimeError):
    """
    Raised when a component fails to receive a required callback
    """
    def __init__(self, obj: str, callback: str):
        self.obj = obj
        self.callback = callback
        super().__init__(f"Failed to inject required callback {self.callback} into {self.obj}")


class InjectionError(RuntimeError):
    """
    Raised when the controller fails to inject or a component fails
    to receive a required callback.
    """
    def __init__(self, component: str, callback: str):
        self.component = component
        self.callback = callback
        super().__init__(f"Failed to inject {self.callback} into {self.component}")


class NoOptionalCallbackWarning(UserWarning):
    """
    Raised when an optional callback was not available
    """
    def __init__(self, component: str, callback: str):
        self.component = component
        self.callback = callback
        super().__init__(f"Component {self.component} requested an optional callback with tag {self.callback} but it"
                         f" was not located.")


class NoOptionalCallbackCollectionWarning(UserWarning):
    """
    Raised when an optional callback collection was not available
    """
    def __init__(self, component: str, callback: str):
        self.component = component
        self.callback = callback
        super().__init__(f"Component {self.component} requested an optional callback collection with tag \
        {self.callback} but it was not located.")


class SingularCallbackCollectionWarning(RuntimeWarning):
    """
    Raised when the injector is able to locate only one callback within an optional or approximate
    callback collection request.
    """
    def __init__(self, component: str, callback: str):
        self.component = component
        self.callback = callback
        super().__init__(f"Component {self.component} requested an approximate or optional callback collection with"
                         f" tag {self.callback} but only one callback was located.")


class CallbackKeyWarning(RuntimeWarning):
    """
    Raised when a callback key is not present in the requesting instance
    """
    def __init__(self, instance: Any, key: str):
        self.instance = instance
        self.key = key
        super().__init__(f"Callback key {self.key} is not present in the requesting instance {self.instance}")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Behavior Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class InvalidStateError(RuntimeError):
    """
    Raised when the behavioral state machine or another object encounters an invalid state
    """
    def __init__(self, name: str):
        self.state = name
        super().__init__(f"State {self.state} is invalid")


class InvalidStateEntryError(RuntimeError):
    """
    Raised when the behavioral state machine attempts to enter a state in a manner that cannot possibly be valid
    """
    def __init__(self, name: str):
        self.state = name
        super().__init__(f"State {self.state} cannot be entered")


class InvalidTransitionError(RuntimeError):
    """
    Raised when the behavioral state machine attempts to transition to a state in a manner that cannot possibly be valid
    """
    def __init__(self, name: str):
        self.transition = name
        super().__init__(f"Transition {self.transition} is invalid")


class InvalidBehavioralDesignWarning(RuntimeWarning):
    """
    Raised when the behavioral design is invalid
    """
    def __init__(self):
        super().__init__("Behavioral design is invalid. Please check that each state is connected to at least "
                         "one transition.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Microscope Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class UnsupportedMicroscopeError(RuntimeError):
    """
    Raised when an unsupported microscope is used
    """
    def __init__(self, microscope: str):
        self.microscope = microscope
        super().__init__(f"Microscope {self.microscope} is not supported. "
                         f"Supported microscopes are {SUPPORTED_MICROSCOPES}")


class MicroscopeConstructionError(RuntimeError):
    """
    Raised when no microscopes were constructed
    """


class MicroscopeConnectionError(ConnectionError):
    """
    Raised when a microscope connection fails
    """


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Video / Camera Errors and Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class CameraConstructionError(RuntimeError):
    """
    Raised when cameras were constructed
    """
    def __init__(self, camera_idx: int):
        self.camera_idx = camera_idx
        super().__init__(f"The following cameras were not constructed: {self.camera_idx}")


class CameraCollectionWarning(RuntimeWarning):
    """
    Raised when camera fails to read a frame

    """
    def __init__(self, camera_idx: str):
        self.camera_idx = camera_idx
        super().__init__(f"Failed to read frame from camera {self.camera_idx}")


class NoCamerasWarning(UserWarning):
    """
    Raised when no cameras were included in video configuration
    """
    def __init__(self):
        super().__init__("If 'use_video' is true in VideoConfigTemplate, "
                         "then at least one camera must be included.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// National Instruments DAQ Errors & Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Speaker Errors & Warnings
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class SpeakerSearchError(KeyError):
    """
    Raised when speaker was not constructed
    """
    def __init__(self, speaker_id: str, found_speakers: dict):
        self.speaker_id = speaker_id
        super().__init__(f"Speaker was not found using the following search id: {self.speaker_id}. These speakers"
                         f" are available {found_speakers.keys()}")


class SpeakerPropertyError(ValueError):
    """
    Raised when selected speaker has an invalid property
    """
    def __init__(self, speaker_id: str, property_name: str, property_value: Any, expected_value: Any):
        self.speaker_id = speaker_id
        self.property_name = property_name
        self.property_value = property_value
        self.expected_value = expected_value
        super().__init__(f"Speaker {self.speaker_id} has an invalid property {self.property_name}. "
                         f"The property must {self.property_value} is not supported: expected {self.expected_value}")


class SpeakerVolumeWarning(RuntimeWarning):
    """
    Raised when speaker volume is out of range
    """
    def __init__(self, request: float, min_request: float, max_request: float, set_volume: float):
        self.request = request
        self.min_request = min_request
        self.max_request = max_request
        self.set_volume = set_volume
        super().__init__(f"Speaker volume request {self.request} decibels generates out of range volume. Minimum volume"
                         f" is {self.min_request} decibels and maximum volume is {self.max_request} decibels. "
                         f"setting to {self.set_volume} decibels instead")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// TIME ERRORS & WARNINGS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class TimeUnitParsingWarning(UserWarning):
    """
    Raised when the time unit is not recognized
    """
    def __init__(self, unit: str):
        self.unit = unit
        super().__init__(f"Time unit {self.unit} is not recognized. Defaulting to microseconds.")


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CONTAINER ERRORS & WARNINGS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class ItemNotAddedWarning(UserWarning):
    """
    Raised when an item is not added to the container
    """
    def __init__(self, item: object):
        self.item = item
        super().__init__(f"Item {self.item} was not added to the container")
