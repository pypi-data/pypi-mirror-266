from abc import ABC, abstractmethod
from collections import ChainMap
from copy import deepcopy
from datetime import datetime
from inspect import getmembers, isclass, isabstract, get_annotations
from pathlib import Path
import sys
from typing import Tuple, Any, Optional, Union, Callable, List
import warnings

from frozendict import frozendict
from nidaqmx.utils import flatten_channel_string
import numpy as np
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field, model_validator
import tomli
import tomli_w

from .exceptions import (DualUserInterfaceError, HeadlessWarning, ImmutableInstanceWarning,
                         UnsupportedMicroscopeError, VersionBackwardCompatibilityError,
                         VersionForwardCompatibilityWarning, VersionBackwardCompatibilityWarning, UpdateVersionWarning)
from .meta import version
from .static import STATIC_PATH, SUPPORTED_MICROSCOPES, DEFAULT_GUI_SETTINGS
from .timing import Time, Milliseconds, Seconds
from .tools import (convert_permitted_types_to_required, FORMAT_TERMINAL, validate_extension, validate_filename, HAS,
                    EMPTY, random_shuffle, balanced_shuffle)


"""
The primary configuration is composed of a base template containing required information, and a tuple of
sub-configurations for components, adapters, and stimuli. The configuration template provides some methods for
verbose printing and user-oriented type-hinting. All configurations are based on the Pydantic BaseModel, which provides
a lot of functionality for free. Configurations can be written to or read from TOML.
"""


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CONFIG TEMPLATE & UTILITIES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class ConfigTemplate(ABC, BaseModel):
    """
    Base Configuration Template. Extends pydantic base models with runtime type-checking when setting attributes and
    verbose type-hinting.
    """
    ###################################################################################################################
    # PYDANTIC CONFIGURATION..
    ###################################################################################################################
    model_config = ConfigDict(validate_assignment=True,
                              arbitrary_types_allowed=True,
                              strict=False,
                              extra="ignore",
                              frozen=False,
                              )

    ###################################################################################################################
    # CONFIGURATION CONSTANTS
    ###################################################################################################################
    version: str = Field(version, title="neurobeam version", description="Version of neurobeam package")

    def __str__(self) -> str:
        """
        Modified dunder method such that the printing is more verbose and easier for human consumption

        Prints the dataclass name and each of its parameters, their values, and associated types

        """
        string_to_print = ""
        for key, value in vars(self).items():
            if key == "components":
                if HAS(value):
                    for sub_config in value:
                        string_to_print += FORMAT_TERMINAL(f"{sub_config.__class__.__name__.replace('Config', '')}\n",
                                                           "component")
                        string_to_print += sub_config.__str__()
                else:
                    string_to_print += FORMAT_TERMINAL(f"{key}", "BLUE")
                    string_to_print += ":None\n"
            elif key == "adapters":
                if HAS(value):
                    for sub_config in value:
                        string_to_print += FORMAT_TERMINAL(f"{sub_config.__class__.__name__.replace('Config', '')}\n",
                                                           "adapter")
                        string_to_print += sub_config.__str__()
                else:
                    string_to_print += FORMAT_TERMINAL(f"{key}", "GREEN")
                    string_to_print += ":None\n"
            elif key in ("states", "transitions"):
                if HAS(value):
                    for sub_config in value:
                        string_to_print += FORMAT_TERMINAL(f"{sub_config.__class__.__name__.replace('Config', '')}\n",
                                                           "behavior")
                        string_to_print += sub_config.__str__()
                else:
                    string_to_print += FORMAT_TERMINAL(f"{key}", "ORANGE")
                    string_to_print += ":None\n"
            elif isinstance(value, (frozendict, dict)):
                # Not robust to nesting
                string_to_print += FORMAT_TERMINAL(f"{key}", "emphasis")
                string_to_print += ":"
                for nested_key in self.__dict__.get(key) if HAS(self.__dict__.get(key)) else {}:
                    string_to_print += f"\n\t{nested_key}: {self.__dict__.get(key).get(nested_key)}"
                string_to_print += "\n"
            else:
                string_to_print += FORMAT_TERMINAL(f"{key}", "emphasis")
                string_to_print += ":"
                string_to_print += f" {self.__dict__.get(key)}\n"

        return string_to_print

    @staticmethod
    @abstractmethod
    def __name__() -> str:
        return "Configuration Template"

    @staticmethod
    def _recursive_coerce(data: Any) -> dict:
        """
        Recursively coerce mutable to immutable

        :param data: The data to coerce
        :returns: Immutable data
        """
        if isinstance(data, (dict, frozendict)):
            data = frozendict({key: ConfigTemplate._recursive_coerce(value) for key, value in data.items()})
        elif isinstance(data, list):
            data = tuple([ConfigTemplate._recursive_coerce(value) for value in data])
        return data

    @classmethod
    def collect_annotations(cls: "ConfigTemplate") -> dict:
        """
        Collects annotations from all parent classes for type-checking

        :returns: Dictionary containing key-type pairs

        """
        return dict(ChainMap(*(get_annotations(cls_) for cls_ in cls.__mro__)))
    # It feels dumb to wrap with dict but for whatever reason it seems to be ordering it which is nice

    # noinspection PyNestedDecorators
    @field_validator("version")
    @classmethod
    def validate_version_compatibility(cls: "ConfigTemplate", v: str) -> str:
        """
        Validate the compatibility of the configuration version with the package version

        :param v: Configuration version
        :returns: Validated configuration version
        :raises VersionForwardCompatibilityWarning: Raised if the configuration major version is ahead of the package
            major version
        :raises VersionBackwardCompatibilityError: Raised if the configuration major version is behind the package
            major version
        :raises VersionBackwardCompatibilityWarning: Raised if the configuration patch version is behind the package
            patch version
        :raises UpdateVersionWarning: Raised if the configuration patch version is ahead of the package patch version
        """
        config_major, config_minor, config_patch = v.split(".")
        package_major, package_minor, package_patch = version.split(".")
        if int(config_major) < int(package_major):
            warnings.warn(VersionForwardCompatibilityWarning(v, version), stacklevel=2)
        elif int(config_major) > int(package_major):
            raise VersionBackwardCompatibilityError(v, version)
        elif int(config_minor) > int(package_minor):
            warnings.warn(VersionBackwardCompatibilityWarning(v, version), stacklevel=2)
        elif int(config_patch) > int(package_patch):
            warnings.warn(UpdateVersionWarning(v, version), stacklevel=2)
        return v

    @classmethod
    def __toml_decode__(cls, data: dict) -> "ConfigTemplate":
        """
        Decode a TOML dictionary into a configuration

        :param data: The dictionary containing the serialized configuration
        :returns: A deserialized and instantiated configuration template

        .. seealso:: :func:`decode_toml <neurobeam.configs.decode_toml>`
        """
        return cls(**decode_toml(data))

    def hint_types(self) -> None:
        """
        Print type hints for the configuration
        """
        type_hints = ""
        annotations_ = self.collect_annotations()
        for key_value, key_type in zip(vars(self).items(), annotations_.items()):
            key, value = key_value
            key_, type_ = key_type
            assert key == key_
            if key == "components":
                if HAS(value):
                    for sub_config in value:
                        type_hints += FORMAT_TERMINAL(f"{sub_config.__class__.__name__.replace('Config', '')}\n",
                                                      "component")
                        type_hints += sub_config.hint_types()
            elif key == "adapters":
                if HAS(value):
                    for sub_config in value:
                        type_hints += FORMAT_TERMINAL(f"{sub_config.__class__.__name__.replace('Config', '')}\n",
                                                      "adapter")
                        type_hints += sub_config.hint_types()
            elif key in ("states", "transitions"):
                if HAS(value):
                    for sub_config in value:
                        type_hints += FORMAT_TERMINAL(f"{sub_config.__class__.__name__.replace('Config', '')}\n",
                                                      "behavior")
                        type_hints += sub_config.hint_types()
            elif "typing.Optional" in f"{type_}":
                type_hints += FORMAT_TERMINAL(f" Optional[{type_.__args__[0].__name__}]\n", "type")
            else:
                type_hints += FORMAT_TERMINAL(f"{key}", "emphasis")
                type_hints += ":"
                type_hints += FORMAT_TERMINAL(f" {type_.__name__}\n", "type")
        print(type_hints)

    def save(self, save_location: Union[str, Path]) -> None:
        """
        Save the configuration to a TOML file
        """
        save_config(save_location, self)

    @model_validator(mode="before")
    def _coerce_mutable(self) -> "ConfigTemplate":
        """
        Coerce mutable fields to immutable types

        :returns: Immutable configuration
        """
        for key, value in self.items():
            if isinstance(value, (dict, frozendict, list)):
                self[key] = ConfigTemplate._recursive_coerce(value)
        return self

    def __toml_encode__(self) -> dict:
        """
        Recursively encode the configuration into a TOML-serializable dictionary

        :returns: The dictionary containing the serialized configuration
        """
        return encode_toml(vars(self))


class _ConfigTemplateFactory:
    """
    Config Template Factory
    """
    #: dict: registry of component template models
    __registry = {}

    @classmethod
    def register_template(cls):  # noqa: ANN001, ANN201, ANN206
        """
        Register a config template with the factory.
        """
        def register_model(config_template):  # noqa: ANN001, ANN201, ANN206
            factory_key = config_template.__fields__.get("factory_key").default
            cls.__registry[factory_key] = config_template
            return config_template
        return register_model

    @classmethod
    def is_config_template(cls, data: Any) -> bool:
        """
        Check if a config template is in the registry
        """
        if isinstance(data, dict) and "factory_key" in data:
            return data.get("factory_key") in cls.__registry

    @classmethod
    def construct_model(cls, data: dict) -> "ConfigTemplate":
        """
        Construct a config template from the deserialized dictionary and the factory key
        """
        factory_key = data.get("factory_key")
        if factory_key not in cls.__registry:
            raise KeyError(f"Factory key {factory_key} not found in registry")
        return cls.__registry[factory_key](**data)

    @classmethod
    def get_config_template(cls, factory_key: str) -> "ConfigTemplate":
        """
        Get a config template from the registry
        """
        if factory_key not in cls.__registry:
            raise KeyError(f"Factory key {factory_key} not found in registry")
        return cls.__registry[factory_key]


class HoistedConfig:
    """
    :class:`Config <neurobeam.configs.Config>` with a specific sub-configuration hoisted to the top-level of the namespace

    :param config: The top-level namespace
    :param key: The field to hoist
    :param idx: The index within the field to hoist

    .. seealso:: :class:`Config <neurobeam.configs.Config>`
    .. seealso:: :class:`ConfigTemplate <neurobeam.configs.ConfigTemplate>`
    """
    def __init__(self, config: "Config", key: str, idx: Optional[int] = None):
        #: Config: The top-level namespace, a Config instance
        self.config = config
        #: ConfigTemplate: The hoisted sub-configuration
        self.hoisted = getattr(config, key)[idx] if HAS(idx) else getattr(config, key)

    def __getattr__(self, item: str) -> Any:
        """
        Get an attribute from the hoisted sub-configuration, and if it doesn't exist, get it from the top-level

        :param item: The attribute to get
        :returns: The attribute from the hoisted sub-configuration
        :raises AttributeError: Raised if the attribute is not found in the hoisted or top-level configuration
        """
        try:
            return getattr(self.hoisted, item)
        except AttributeError:
            return getattr(self.config, item)


def decode_toml(data: dict) -> Union[dict, "ConfigTemplate"]:
    """
    Recursively decode a TOML-serialized dictionary into a configuration

    :param data: The dictionary to decode
    :returns: The deserialized dictionary
    """
    decoding = deepcopy(data)  # Avoid modifying the original dictionary
    for key, value in decoding.items():
        # Check if component template
        if _ConfigTemplateFactory.is_config_template(value):
            return _ConfigTemplateFactory.construct_model(decode_toml(value))
        # Check if sub-configuration
        elif key in ("components", "adapters", "states", "transitions", "stimuli") and isinstance(value, dict):
            decoding[key] = tuple([decode_toml({key: sub_value}) for key, sub_value in value.items()])
        # check if frozendict
        elif isinstance(value, dict):
            decoding[key] = frozendict(value)
        elif isinstance(value, list):
            if len(value) == 2 and isinstance(value[0], (int, float)) and isinstance(value[1], str):
                decoding[key] = Time.__toml_decode__(value)
            else:
                decoding[key] = tuple(value)
        # check if None
        elif value == "NULL":
            decoding[key] = None
        else:
            pass
    return decoding


def encode_toml(data: dict) -> dict:
    """
    Recursively encode a dictionary into a TOML-serializable dictionary

    :param data: The dictionary to encode
    :returns: The TOML-serializable dictionary
    """
    encoding = deepcopy(data)  # Avoid modifying the original dictionary
    for key, value in encoding.items():
        if isinstance(value, ConfigTemplate):
            encoding[key] = encode_toml(vars(value))
        elif isinstance(value, Time):
            encoding[key] = value.__toml_encode__()
        # for config template tuples/sets
        elif isinstance(value, (tuple, set)) and all(isinstance(sub_value, ConfigTemplate) for sub_value in value):
            encoding[key] = {f"{idx}": encode_toml(vars(sub_value)) for idx, sub_value in enumerate(value)}
        # for other tuples/sets
        elif isinstance(value, (tuple, set)) and not all(isinstance(sub_value, ConfigTemplate) for sub_value in value):
            encoding[key] = [str(val) for val in value]
        elif isinstance(value, np.ndarray):
            encoding[key] = [str(val) for val in value.tolist()]
        elif isinstance(value, frozendict):
            encoding[key] = dict(value)
        elif EMPTY(value):
            encoding[key] = "NULL"
        else:
            encoding[key] = str(value)
    return encoding


@convert_permitted_types_to_required(permitted=(str, Path), required=Path, pos=0, key="path")
@validate_extension(required_extension=".toml", pos=0, key="path")
def load_config(path: Path) -> "ConfigTemplate":
    """
    Load a configuration from a TOML file

    :param path: The path to load configuration from
    :returns: The configuration loaded from the file
    """
    with open(path, "rb") as file:
        data = tomli.load(file)
        if "factory_key" in data:
            cls = _ConfigTemplateFactory.get_config_template(data.get("factory_key"))
            return cls.__toml_decode__(data)
        else:
            return Config.__toml_decode__(data)


@convert_permitted_types_to_required(permitted=(str, Path), required=Path, pos=0, key="path")
@validate_filename(pos=0, key="path")
@validate_extension(required_extension=".toml", pos=0, key="path")
def save_config(path: Path, config: "ConfigTemplate") -> None:
    """
    Saves a configuration to a TOML file

    :param path: The path to save configuration
    :param config: The configuration to save
    """

    with open(path, "wb") as file:
        tomli_w.dump(config.__toml_encode__(), file)


@convert_permitted_types_to_required(permitted=(str, Path), required=Path, pos=0, key="path")
def generate_default_configs(path: Path = STATIC_PATH, target: Optional[Union[str, "ConfigTemplate"]] = None) -> None:
    """
    Generate default configurations

    :param path: The path to save configurations
    :param target: The name of a specific configuration to generate default for (e.g., "Config")
    """
    config_module = sys.modules[__name__]
    if isclass(target) and issubclass(target, ConfigTemplate) and not isabstract(target):
        # noinspection PyCallingNonCallable
        save_config(path.joinpath(f"{target.__name__}.toml"), target())
    else:
        for name, cls in getmembers(config_module, isclass):
            if issubclass(cls, ConfigTemplate) and not isabstract(cls):
                if target is None or target == name:
                    save_config(path.joinpath(f"{name}.toml"), cls())


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CALLBACK REQUESTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@_ConfigTemplateFactory.register_template()
class CallbackRequestConfig(ConfigTemplate):

    factory_key: str = Field("CallbackRequest", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    key: Union[str, Tuple[str, ...]] = Field("callback",
                                             title="key",
                                             description="Key/s for the callback request")

    approximate: bool = Field(False,
                              title="approximate",
                              description="Boolean indicating whether to retrieve the callback as an approximate match")

    required: bool = Field(False, title="required",
                           description="Boolean indicating whether the callback is required")

    arguments: Optional[Union[frozendict[str, Any], Tuple[frozendict[str, Any]]]] =\
        Field(None, title="arguments", description="Any keyword arguments for the callback")

    wildcard: Optional[Union[Tuple[str, Any], Tuple[Tuple[str, Any], ...]]] \
        = Field(None, title="wildcard", description="wildcard")

    @staticmethod
    def __name__() -> str:
        return "Callback Request Configuration"


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// COMPONENT SUB-CONFIGURATIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


# noinspection PyNestedDecorators
@_ConfigTemplateFactory.register_template()
class CameraConfig(ConfigTemplate):
    """
    Sub-configuration for creating camera components.

    .. seealso:: :class:`ConfigTemplate <neurobeam.configs.ConfigTemplate>`
    .. seealso:: :class:`Camera <neurobeam.hardware.video.Camera>`
    .. seealso:: :class:`VideoFeed <prove.hardware.video.VideoFeed>`
    """
    factory_key: str = Field("Camera", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    # note that there isn't a clear way to get the opencv id using the MSMF backend & it's a bit of a pain to set up,
    # however microsoft recommends using the MSMF backend and it supports hardware-acceleration
    camera_idx: int = Field(0, title="camera_idx", description="OpenCV index of camera to use", ge=0)

    save_video: bool = Field(True,
                             title="save_feed",
                             description="Boolean indicating whether to save camera feed to file")

    height: int = Field(480, title="height", description="Height of camera frame", ge=1)

    width: int = Field(640, title="width", description="Width of camera frame", ge=1)

    fps: float = Field(30.0, title="fps", description="Frames per second of camera", gt=0)

    @staticmethod
    def __name__() -> str:
        return "Camera Configuration"


# noinspection PyNestedDecorators
@_ConfigTemplateFactory.register_template()
class DAQConfig(ConfigTemplate):
    """
    Sub-configuration for creating DAQ components.

    .. seealso:: :class:`ConfigTemplate <neurobeam.configs.ConfigTemplate>`
    .. seealso:: :class:`DAQ <neurobeam.hardware.daq.DAQ>`
    """
    factory_key: str = Field("DAQ", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    device_id: str = Field("SimDAQ", title="device_id", description="Name of National Instruments DAQ")

    timeout: float = Field(1.0,
                           title="timeout",
                           description="Timeout for all DAQ interactions (s)",
                           gt=0.0)

    sampling_frequency: int = Field(1000,
                                    title="sampling_frequency",
                                    description="Sampling frequency (Hz) for hardware-timed DAQ streams",
                                    ge=1,
                                    le=10000)

    buffer_frequency: int = Field(100,
                                  title="buffer_frequency",
                                  description="Buffering frequency (Hz) for hardware-timed DAQ streams")

    digital_analog_sampling_ratio: float = (
        Field(0.5,
              title="digital_analog_sampling_ratio",
              description="Ratio of software-timed digital to hardware-timed analog samples",
              gt=0.0,
              lt=1.0))

    analog_input_index: frozendict[str, int] = (
        Field(frozendict({"imaging_start": 0,
                          "linear_actuator_position": 1,
                          "wheel_position": 2,
                          "burrow_tension": 3,
                          "locomotion": 4}),
              title="analog_input_index",
              description="Mapping of analog input keys to physical indices"))

    analog_input_range: Tuple[float, float] = Field(default=(-10.0, 10.0),
                                                    title="analog_input_range",
                                                    description="Range of permissible analog input voltage ranges")

    analog_output_index: frozendict[str, int] = (
        Field(frozendict({"stimulus": 0, "linear_actuator": 1}),
              title="analog_output_index",
              description="Mapping of analog output keys to physical indices"))

    analog_output_range: frozendict[str, Tuple[float, float]] = (
        Field(frozendict({"stimulus": (0.0, 5.0), "linear_actuator": (0.0, 5.0)}),
              title="analog_output_range",
              description="Mapping of analog output keys to permissible output voltage ranges"))

    digital_input_index: frozendict[str, Tuple[int, int]] = (
        Field(frozendict(
            {"burrow_sensor": (0, 0),
             "reward_sucrose": (0, 1),
             "reward_water": (0, 2),
             "licking_sucrose": (0, 3),
             "licking_water": (0, 4)}),
            title="digital_input_index",
            description="Mapping of digital input keys to physical indices"))

    digital_output_index: frozendict[str, Tuple[int, int]] = (
        Field(frozendict({
            "burrow_sensor_driver": (0, 5),
            "event_indicator": (0, 6),
            "trial_indicator": (0, 7),
            "permit_water_reward": (1, 0),
            "permit_sucrose_reward": (1, 1),
            "rotate_spouts": (1, 2),
            "remove_spouts": (1, 3),
            "wet_start": (2, 0)
        }),
            title="digital_output_index",
            description="Mapping of digital output keys to physical indices"))

    @computed_field
    @property
    def analog_buffer_size(self) -> int:
        """
        Size of analog buffer in samples

        """

        return self.sampling_frequency // self.buffer_frequency

    @computed_field
    @property
    def digital_buffer_size(self) -> int:
        """
        Size of digital buffer in samples

        """
        return round(self.sampling_frequency / self.buffer_frequency)

    @computed_field
    @property
    def analog_output_channels(self) -> dict:
        return {key: "".join([self.device_id, "/ao", str(self.analog_output_index.get(key))]) for key in
                self.analog_output_index.keys()}

    @computed_field
    @property
    def analog_output_cids(self) -> Tuple[str, ...]:
        return self.analog_output_index.keys()

    @computed_field
    @property
    def num_analog_output_channels(self) -> int:
        return len(self.analog_output_index.keys())

    @computed_field
    @property
    def flattened_analog_outputs(self) -> str:
        return flatten_channel_string([self.analog_output_channels.get(key)
                                       for key in self.analog_output_channels.keys()])

    @computed_field
    @property
    def analog_input_channels(self) -> dict:
        return {key: "".join([self.device_id, "/ai", str(self.analog_input_index.get(key))]) for key in
                self.analog_input_index.keys()}

    @computed_field
    @property
    def analog_input_cids(self) -> Tuple[str, ...]:
        return self.analog_input_index.keys()

    @computed_field
    @property
    def num_analog_input_channels(self) -> int:
        return len(self.analog_input_index.keys())

    @computed_field
    @property
    def flattened_analog_inputs(self) -> str:
        return flatten_channel_string([self.analog_input_channels.get(key)
                                       for key in self.analog_input_channels.keys()])

    @computed_field
    @property
    def digital_input_channels(self) -> dict:
        return {key: "".join([
            self.device_id, "/port", str(self.digital_input_index.get(key)[0]), "/line",
            str(self.digital_input_index.get(key)[1])]) for key in self.digital_input_index.keys()}

    @computed_field
    @property
    def digital_input_cids(self) -> Tuple[str, ...]:
        return self.digital_input_index.keys()

    @computed_field
    @property
    def num_digital_input_channels(self) -> int:
        return len(self.digital_input_index.keys())

    @computed_field
    @property
    def flattened_digital_inputs(self) -> str:
        return flatten_channel_string([self.digital_input_channels.get(
            key) for key in self.digital_input_channels.keys()])

    @computed_field
    @property
    def digital_output_channels(self) -> dict:
        return {key: "".join([self.device_id, "/port", str(self.digital_output_index.get(key)[0]), "/line",
                              str(self.digital_output_index.get(key)[1])]) for key in self.digital_output_index.keys()}

    @computed_field
    @property
    def num_digital_output_channels(self) -> int:
        return len(self.digital_output_index.keys())

    @computed_field
    @property
    def flattened_digital_outputs(self) -> str:
        return flatten_channel_string([self.digital_output_channels.get(key)
                                       for key in self.digital_output_channels.keys()])

    @staticmethod
    def __name__() -> str:
        return "Hardware Configuration"

    @model_validator(mode="after")
    def _validate_analog_output_mapping(self) -> "DAQConfig":
        assert set(self.analog_output_index.keys()) == set(self.analog_output_range.keys()), \
            "Analog output index and range mappings must have the same keys"
        return self

    @model_validator(mode="after")
    def _validate_index_mapping(self) -> "DAQConfig":
        mappings = [self.analog_input_index,
                    self.analog_output_index,
                    self.digital_input_index,
                    self.digital_output_index]
        keys = [key for mapping in mappings for key in mapping.keys()]
        assert len(keys) == len(set(keys)), "Keys must be unique"
        return self

    @model_validator(mode="after")
    def _validate_effective_sampling(self) -> "DAQConfig":
        if self.sampling_frequency % self.buffer_frequency != 0:
            raise AssertionError(f"Buffer size must be int: {self.sampling_frequency=}, {self.buffer_frequency=}, "
                                 f"buffer size={self.sampling_frequency / self.buffer_frequency}")
        if self.buffer_frequency > self.sampling_frequency:
            raise AssertionError(f"Buffer frequency must be less than or equal to sampling frequency: "
                                 f"{self.sampling_frequency=}, {self.buffer_frequency=}")

        return self


# noinspection PyNestedDecorators
@_ConfigTemplateFactory.register_template()
class MicroscopeConfig(ConfigTemplate):
    """
    Sub-configuration for creating microscope components.

    .. seealso:: :class:`ConfigTemplate <neurobeam.configs.ConfigTemplate>`
    .. seealso:: :class:`Microscope <neurobeam.hardware.microscopes.Microscope>`
    """
    factory_key: str = Field("Microscope", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    software: str = Field("PrairieView",
                          title="brand",
                          description="Name of the microscope software")

    realtime_mode: bool = Field(False,
                                title="realtime_mode",
                                description="Boolean indicating whether to interface in realtime mode")

    motion_correction: bool = Field(False,
                                    title="motion_correction",
                                    description="Boolean indicating whether to motion correct images online")

    identify_rois: bool = Field(False,
                                title="identify_rois",
                                description="Boolean indicating whether to identify ROIs online")

    extract_fluorescence: bool = Field(False,
                                       title="extract_fluorescence",
                                       description="Boolean indicating whether to extract fluorescence online")

    infer_spikes: bool = Field(False,
                               title="infer_spikes",
                               description="Boolean indicating whether to infer spikes online")

    monitor_ensembles: bool = Field(False,
                                    title="monitor_ensembles",
                                    description="Boolean indicating whether to monitor ensemble activity online")

    @staticmethod
    def __name__() -> str:
        return "Microscope Configuration"

    @field_validator("software")
    @classmethod
    def _validate_brand(cls: "MicroscopeConfig", v: str) -> str:
        """
        Validate the microscope software brand

        :param v: The microscope software brand
        :returns: Validated microscope software brand
        """
        if not any((v.lower() in scope.lower() for scope in SUPPORTED_MICROSCOPES)):
            raise UnsupportedMicroscopeError(v)
        return v

    @model_validator(mode="after")
    def _warn_implemented_settings(self) -> "MicroscopeConfig":
        """
        Warn if the selected settings are not implemented in this version of the software

        :returns: Validated settings
        """
        for key, value in vars(self).items():
            if key in ("motion_correction",
                       "identify_rois",
                       "extract_fluorescence",
                       "infer_spikes",
                       "monitor_ensembles",
                       "realtime_mode"):
                if value:
                    warnings.warn(VersionBackwardCompatibilityWarning(key, value), stacklevel=2)
        return self


# noinspection PyNestedDecorators
@_ConfigTemplateFactory.register_template()
class SLMConfig(ConfigTemplate):
    """
    Sub-configuration for creating photostimulation components.

    .. seealso:: :class:`ConfigTemplate <neurobeam.configs.ConfigTemplate>`
    .. seealso:: :class:`SLM <neurobeam.hardware.slm.SLM>`
    """
    factory_key: str = Field("SLM", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    brand: str = Field("Meadowlark", title="brand", description="Name of the spatial light modulator brand")

    realtime_mode: bool = Field(False,
                                title="realtime_mode",
                                description="Boolean indicating whether to interface in realtime mode")

    @staticmethod
    def __name__() -> str:
        return "SLM Configuration"

    @model_validator(mode="after")
    def _warn_implemented_settings(self) -> "SLMConfig":
        """
        Warn if the selected settings are not implemented in this version of the software

        :returns: Validated settings
        """
        for key, value in vars(self).items():
            if key in ("realtime_mode", ):
                if value:
                    warnings.warn(VersionBackwardCompatibilityWarning(key, value), stacklevel=2)
        return self


# noinspection PyNestedDecorators
@_ConfigTemplateFactory.register_template()
class SpeakerConfig(ConfigTemplate):
    """
    Sub-configuration for creating speaker components.

    .. seealso:: :class:`ConfigTemplate <neurobeam.configs.ConfigTemplate>`
    .. seealso:: :class:`Speaker <neurobeam.hardware.speakers.Speaker>`
    """
    factory_key: str = Field("Speaker", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    speaker_id: str = Field("Speakers (High Definition", title="speaker_id",
                            description="Name of audio output device")

    volume: float = Field(1.0, title="volume", description="Volume of audio output", ge=0.0, le=1.0)

    lut: Optional[frozendict[str, float]] = Field(None, title="lut",
                                                  description="Lookup table for audio intensity")

    @staticmethod
    def __name__() -> str:
        return "Speaker Configuration"

    @field_validator("lut")
    @classmethod
    def _validate_lut(cls: "SpeakerConfig", v: Union[Path, frozendict[str, np.ndarray]]) \
            -> Union[Path, frozendict[str, np.ndarray]]:
        """
        Validate the lookup table for audio intensity

        :param v: The lookup table
        :returns: The validated lookup table
        """
        if isinstance(v, Path):
            v = np.load(v, allow_pickle=True).item()
        if HAS(v):
            return {str(key): value for key, value in v.items()}


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ADAPTER SUB-CONFIGURATIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@_ConfigTemplateFactory.register_template()
class AnalogPulseConfig(ConfigTemplate):
    factory_key: str = Field("AnalogPulse", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    name: str = Field("Analog Pulse", title="name", description="Name of the analog pulse")

    device_id: str = Field("SimDAQ",
                           title="device_id",
                           description="Name of DAQ implementing the linear actuator")

    analog_pulse_channel_key: str = Field("analog_pulse",
                                          title="analog_pulse_channel_key",
                                          description="Key for the pulse output channel")

    @staticmethod
    def __name__() -> str:
        return "Analog Pulse Configuration"


@_ConfigTemplateFactory.register_template()
class AudioStimulusConfig(ConfigTemplate):
    """
    Sub-configuration for creating auditory stimuli adapters
    """
    factory_key: str = Field("AudioStimulus", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    name: str = Field("Audio Stimulus", title="name", description="Name of the audio stimulus")

    device_id: str = Field("Digital",
                           title="device_id",
                           description="Name of Speaker implementing the audio stimulus")

    style: str = Field("white_noise", title="style", description="Type of audio stimulus")

    duration: Time = Field(Seconds(1), title="duration", description="Duration of the audio stimulus")

    options: Optional[frozendict[str, Any]] = Field(None,
                                                    title="options",
                                                    description="Any additional keyword options for the stimulus")

    @staticmethod
    def __name__() -> str:
        return "Audio Stimulus Configuration"


@_ConfigTemplateFactory.register_template()
class LinearActuatorConfig(ConfigTemplate):
    """
    Sub-configuration for creating linear actuator adapters.
    """
    factory_key: str = Field("LinearActuator", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    name: str = Field("Linear Actuator", title="name", description="Name of the linear actuator")

    device_id: str = Field("SimDAQ",
                           title="device_id",
                           description="Name of DAQ implementing the linear actuator")

    command_channel_key: str = Field("linear_actuator",
                                     title="command_channel_key",
                                     description="Key for the linear actuator output channel")

    physical_range: Tuple[float, float] = Field((0.0, 50.0),
                                                title="physical_range",
                                                description="Physical range of the linear actuator")

    physical_units: str = Field("mm",
                                title="physical_units",
                                description="Physical units of the linear actuator range")

    @staticmethod
    def __name__() -> str:
        return "Linear Actuator Configuration"


@_ConfigTemplateFactory.register_template()
class StimulusTriggerConfig(ConfigTemplate):
    """
    Sub-configuration for creating stimulus trigger adapters.
    """
    factory_key: str = Field("StimulusTrigger", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    name: str = Field("Stimulus Trigger", title="name", description="Name of the stimulus trigger")

    stimulus_name: str = Field("AudioStimulus",
                               title="stimulus_name",
                               description="Name of the stimulus to trigger")

    relative_onset: Time = Field(Seconds(0), title="relative_onset", description="Relative onset of the trigger")

    @staticmethod
    def __name__() -> str:
        return "Stimulus Trigger Configuration"


@_ConfigTemplateFactory.register_template()
class DigitalTriggerConfig(ConfigTemplate):
    """
    Sub-configuration for creating digital trigger adapters.
    """
    factory_key: str = Field("DigitalTrigger", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor. "
                                         "Identical to the name of the implementing class")

    name: str = Field("Digital Trigger", title="name", description="Name of the digital trigger")

    device_id: str = Field("SimDAQ",
                           title="device_id",
                           description="Name of DAQ implementing the digital trigger")

    digital_trigger_channel_key: str = Field("digital_trigger",
                                             title="digital_trigger_channel_key",
                                             description="Key for the digital trigger channel")

    @staticmethod
    def __name__() -> str:
        return "Digital Trigger Configuration"


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// BEHAVIOR CONFIGURATION & SUB-CONFIGURATIONS (TECHNICALLY A COMPONENT SUB-CONFIGURATION WITH SUB-CONFIGURATIONS)
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@_ConfigTemplateFactory.register_template()
class StateConfig(ConfigTemplate):
    factory_key: str = Field("State", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor."
                                         "Identical to the name of the implementing class")

    name: str = Field("State", title="name", description="Name of the state")

    duration: Optional[Time] = Field(None, title="duration", description="Duration of the state")

    entry_callbacks: Optional[Union[CallbackRequestConfig, Callable, Tuple[Callable, ...]]] \
        = Field(None, title="entry_callbacks", description="Entry callbacks")
    exit_callbacks: Optional[Union[CallbackRequestConfig, Callable, Tuple[Callable, ...]]] \
        = Field(None, title="exit_callbacks", description="Exit callbacks")

    triggers: Optional[List[Tuple[str, Tuple[str, str]]]] = Field(None,
                                                                  title="triggers",
                                                                  description="Triggers for the state")

    special: Optional[str] = Field(None, title="special", description="keyword of a special state implementation")

    options: Optional[frozendict[str, Any]] = Field(None,
                                                    title="options",
                                                    description="Additional options for a special state")

    @staticmethod
    def __name__() -> str:
        return "State Configuration"


@_ConfigTemplateFactory.register_template()
class TransitionConfig(ConfigTemplate):
    factory_key: str = Field("Transition", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor."
                                         "Identical to the name of the implementing class")

    name: str = Field("Auto", title="name", description="Name of the transition")

    origin: str = Field("Setup", title="origin", description="Name of the origin state")

    targets: Union[str, Tuple[str, ...]] = Field("End",
                                                 title="targets",
                                                 description="Names of the target state/s")

    order: Optional[Tuple[int, ...]] = Field(None, title="order", description="Order of the target states")

    final: Optional[str] = Field(None, title="final", description="Name of the final state")

    shuffle_method: Optional[str] = Field(None,
                                          title="shuffle_order",
                                          description="Boolean indicating whether to shuffle the order")
    _shuffled = False

    @staticmethod
    def __name__() -> str:
        return "Transition Configuration"

    @property
    def shuffled(self):
        return self._shuffled

    @shuffled.setter
    def shuffled(self, value: bool):
        self._shuffled = value

    @model_validator(mode="after")
    def _shuffle_order(self) -> "TransitionConfig":
        if HAS(self.shuffle_method) and not self.shuffled:
            if self.shuffle_method == "random":
                self._shuffled = True
                self.order = tuple(random_shuffle(self.order))
            elif self.shuffle_method == "balanced":
                self._shuffled = True
                self.order = tuple(balanced_shuffle(self.order))
            elif self.shuffle_method == "resampled":
                raise NotImplementedError
            else:
                raise NotImplementedError

        return self


@_ConfigTemplateFactory.register_template()
class BehaviorConfig(ConfigTemplate):
    factory_key: str = Field("Behavior", title="factory_key", allow_mutation=False,
                             description="Key used to locate constructor."
                                         "Identical to the name of the implementing class")

    name: str = Field("Behavioral Task", title="name", description="Name of the behavioral task")

    states: Optional[Tuple[StateConfig, ...]] = Field(None, title="states", description="State configurations")

    transitions: Optional[Tuple[TransitionConfig, ...]] = Field(None, title="transitions",
                                                                description="Transition configurations")

    @staticmethod
    def __name__() -> str:
        return "Behavior Configuration"

    def add_state(self, state: "StateConfig") -> None:
        """
        Add a state configuration to the behavior configuration

        :param state: Configuration of the state to add to the behavior

        .. seealso:: :class:`StateConfig <neurobeam.configs.StateConfig>`
        """
        if self.states is None:
            self.states = (state, )
        else:
            self.states += (state, )

    def add_transition(self, transition: "TransitionConfig") -> None:
        """
        Add a transition configuration to the behavior configuration

        :param transition: Configuration of the transition to add to the behavior

        .. seealso:: :class:`TransitionConfig <neurobeam.configs.TransitionConfig>`
        """
        if self.transitions is None:
            self.transitions = (transition, )
        else:
            self.transitions += (transition, )


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PROBE CONFIGURATION
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


# noinspection PyNestedDecorators
class Config(ConfigTemplate):
    """
    Primary configuration for the neurobeam package. Contains experimental settings, metadata, and (potentially)
    component and adapter sub-configurations.
    """
    ###################################################################################################################
    # EXPERIMENT METADATA (MUTABLE)
    ###################################################################################################################
    subject: str = Field("subject",
                         title="subject",
                         description="Name or ID of the experimental subject")

    experimenter: str = Field("John Doe",
                              title="experimenter",
                              description="Name of the scientist conducting experiment")

    session: int = Field(1,
                         title="session",
                         description="Experiment session number (1-indexed)",
                         ge=0)

    study: str = Field("study", title="study", description="Name or ID of the study")

    condition: str = Field("condition",
                           title="condition",
                           description="Name or ID of the experimental condition")

    notes: Optional[frozendict[str, Any]] = Field(None,
                                                  title="notes",
                                                  description="Notes about the experiment")

    ###################################################################################################################
    # EXPERIMENT METADATA (CONSTANT)
    ###################################################################################################################
    # noinspection PyTypeHints
    date: str = Field(datetime.now().strftime("%Y-%m-%d"),
                      title="date",
                      description="Date of experiment")

    # noinspection PyTypeHints
    timestamp: str = Field(datetime.now().strftime("%H:%M:%S"),
                           title="timestamp",
                           description="Time of experiment")

    ###################################################################################################################
    # EXPERIMENT CONFIGURATION
    ###################################################################################################################
    save_directory: Path = Field(Path.cwd(),
                                 title="save_directory",
                                 description="Directory to save experiment data")

    use_console: bool = Field(True,
                              title="use_console",
                              description="Boolean indicating whether to print progress to console")

    use_gui: bool = Field(False,
                          title="use_gui",
                          description="Boolean indicating whether to launch graphical user interface for experiment")

    gui_settings: Path = Field(DEFAULT_GUI_SETTINGS, title="gui_settings", description="Path to GUI settings file")

    reporting_frequency: float = Field(1.0,
                                       title="reporting_frequency",
                                       description="Frequency of progress reporting")

    ###################################################################################################################
    # SUB-CONFIGURATIONS
    ###################################################################################################################
    components: Optional[Tuple["ConfigTemplate", ...]] = Field(None,
                                                               title="components",
                                                               description="Sub-configurations for neurobeam components")

    adapters: Optional[Tuple["ConfigTemplate", ...]] = Field(None,
                                                             title="adapters",
                                                             description="Sub-configurations for neurobeam adapters")

    def __str__(self):
        string_to_print = FORMAT_TERMINAL(f"{self.__name__()}\n", "header")
        string_to_print += super().__str__()
        return string_to_print

    @computed_field
    @property
    def locked(self) -> bool:
        """
        :Getter: Whether the configuration is locked and immutable
        :Getter Type: bool
        :Setter: Lock the configuration. Cannot be unlocked.
        :Setter Type: bool
        """
        return self.model_config.get("frozen")

    @computed_field
    @property
    def reporting_interval(self) -> Time:
        """
        :Getter: The interval between progress reports (microseconds)
        :Getter Type: Time
        """
        return Seconds(1 / self.reporting_frequency)

    @computed_field
    @property
    def save_location(self) -> Path:
        """
        :Getter: The path to the save location
        :Getter Type: Path
        """
        return self.save_directory.joinpath(
            f"{self.subject.replace(' ', '_')}_"
            f"{self.study.replace(' ', '_')}_"
            f"{self.condition.replace('-', '_')}_"
            f"{self.date.replace('-', '_')}")

    @computed_field
    @property
    def file_header(self) -> str:
        """
        :Getter: The header for filenames
        :Getter Type: str
        """
        return (f"{self.subject.replace(' ', '_')}_"
                f"{self.study.replace(' ', '_')}_"
                f"{self.condition.replace('-', '_')}_"
                f"{self.date.replace('-', '_')}_"
                )

    @staticmethod
    def __name__() -> str:
        return "Probe Configuration"

    @field_validator("save_directory", "gui_settings", mode="before")
    @classmethod
    def _coerce_path(cls: "Config", v: Union[str, Path]) -> Path:
        """
        Coerce a string into a Path object
        :param v: The string to be coerced
        :returns: The string as a Path object
        """
        return Path(v)

    @locked.setter
    def locked(self, value: bool) -> "Config":
        if not self.model_config["frozen"]:
            self.model_config["frozen"] = value
        else:
            warnings.warn(ImmutableInstanceWarning("Configuration is locked and immutable"), stacklevel=1)

    def add_component(self, config: "ConfigTemplate") -> "Config":
        """
        Add a component configuration to the neurobeam configuration

        :param config: The component configuration to add
        :raises: ImmutableInstanceWarning: Raised if the configuration is locked and immutable
        """
        if self.locked:
            warnings.warn(ImmutableInstanceWarning("Configuration is locked and immutable"), stacklevel=2)
        elif self.components is None:
            self.components = (config,)
        else:
            self.components += (config,)

    def add_adapter(self, config: "ConfigTemplate") -> "Config":
        """
        Add an adapter configuration to the neurobeam configuration

        :param config: The adapter configuration to add
        :raises: ImmutableInstanceWarning: Raised if the configuration is locked and immutable
        """
        if self.locked:
            warnings.warn(ImmutableInstanceWarning("Configuration is locked and immutable"), stacklevel=2)
        elif self.adapters is None:
            self.adapters = (config,)
        else:
            self.adapters += (config,)

    def generate_filename(self, name: str, ext: Optional[str] = None) -> Path:
        """
        Generate a filename for a file related to the current configuration

        :param name: The name of the file
        :param ext: The extension of the file
        """
        if EMPTY(ext) and "." in name:
            name, ext = name.split(".")[-2:]
        if "." not in ext:
            ext = f".{ext}"
        filename = self.save_location.joinpath(f"{self.file_header}{name}").with_suffix(ext)
        return filename

    def save(self, save_location: Optional[Union[str, Path]] = None) -> None:
        """
        Save the configuration to a TOML file

        :param save_location: The location to save the configuration
        """
        if HAS(save_location):
            save_config(save_location, self)
        else:
            save_config(self.generate_filename("configuration", ".toml"), self)

    @model_validator(mode="after")
    def _validate_user_interface(self) -> "Config":
        """
        Validate the user interface settings

        :raises DualUserInterfaceError: Raised if both console and GUI are enabled
        :raises HeadlessWarning: Raised if neither console nor GUI are enabled
        """
        if self.use_console and self.use_gui:
            raise DualUserInterfaceError()
        if not self.use_console and not self.use_gui:
            warnings.warn(HeadlessWarning(), stacklevel=2)
        return self
