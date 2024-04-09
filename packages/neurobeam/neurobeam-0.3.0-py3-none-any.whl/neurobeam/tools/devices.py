from typing import Union
import asyncio
import subprocess
from enum import IntEnum
from collections import ChainMap

from winsdk.windows.devices.enumeration import DeviceInformation
from winsdk.windows.media.devices import VideoDeviceController
from frozendict import frozendict
from nidaqmx import system
from psychtoolbox import audio


"""
Tools for locating various devices.
"""


class DeviceClass(IntEnum):
    """
    DeviceClass is an enumeration of the different classes of devices utilized by PROBE.

    The SPEAKER and CAMERA enumerated constants reflect their enumerations in the Windows Runtime API
    'DeviceClass <https://learn.microsoft.com/en-us/uwp/api/windows.devices.enumeration.deviceclass?view=winrt-22621>'.
    This enumeration is outlined below. There is a python-interface for WinRT, but it is unmaintained. The python
    package winsdk is a community-driven fork of WinRT that seems suitable, albeit lightly documented.

    Probe enumerated device class constants
    SPEAKER = 2
    CAMERA = 4
    DAQ = 7
    ALL = 8

    Windows Runtime API DeviceClass Enum
    All = 0
    AudioCapture = 1
    AudioRender = 2
    PortableStorageDevice = 3
    VideoCapture = 4
    ImageScanner = 5
    Location = 6

    """
    SPEAKER = 2
    CAMERA = 4
    DAQ = 7
    ALL = 8

    @classmethod
    def from_string(cls, device_class: str):
        device_class = device_class.upper()
        if device_class in cls.__members__.keys():
            return getattr(cls, device_class)
        else:
            raise ValueError

    @classmethod
    def from_arg(cls, device_class: Union[int, str]):
        if isinstance(device_class, str):
            return cls.from_string(device_class)
        elif isinstance(device_class, int):
            return cls(device_class)
        else:
            raise ValueError


def find_devices(device_class: Union[int, str, "DeviceClass"]) -> Union[frozendict, ChainMap]:
    """
    Finds devices associated with the specified device-class enumerated constant.

    """
    # convert to enumerated constant if int or str
    device_class = DeviceClass.from_arg(device_class)

    # find devices for each type
    if device_class == DeviceClass.SPEAKER:
        return _find_speakers()
    elif device_class == DeviceClass.CAMERA:
        return _find_cameras()
    elif device_class == DeviceClass.DAQ:
        devices = _get_daqs()
    elif device_class == DeviceClass.ALL:
        # get all enumerated device constants except for All, then recursively call find_devices()
        enums = list(DeviceClass.__members__.values())[:-1]
        return ChainMap([find_devices(device_class_) for device_class_ in enums])
    else:
        raise ValueError


def _find_cameras():
    """
    Find cameras using WinRT

    """
    devices = asyncio.run(_get_winrt_devices(DeviceClass.CAMERA))
    return frozendict({device.name: (idx, device) for idx, device in enumerate(devices)})


def _find_speakers() -> frozendict:
    """
    Find speakers using the low-latency Windows Audio Session API (WASAPI) through combination of WinRT &
    psychtoolbox's PsychPortAudio.

    """
    # get speakers using winRT
    devices = asyncio.run(_get_winrt_devices(DeviceClass.SPEAKER))
    # make mapping
    devices = {device.name: None for device in devices}
    # pair properties of speaker , device_type 13 flags WASAPI only
    properties = audio.get_devices(device_type=13)
    names = [device.get("DeviceName") for device in properties]
    for device in devices.keys():
        idx = [position for position, string in enumerate(names) if string.lower() in device.lower()]
        devices[device] = properties[idx[-1]]   # If audio.get_devices erroneously returns high and
        # low-latency implementations, the low-latency implementation will be second
    return frozendict(devices)


async def _get_winrt_devices(device_class: int):
    return await DeviceInformation.find_all_async(device_class)


def _get_daqs():
    devices = system.System.local().devices
    return frozendict({device.name: device.product_type for device in devices})
