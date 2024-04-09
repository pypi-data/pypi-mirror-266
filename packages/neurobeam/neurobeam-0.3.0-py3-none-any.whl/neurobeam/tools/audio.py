from typing import Tuple  # Optional
from functools import partial

import numpy as np

from ..registries import AudioRegistry
from ..timing import Time
from .readability import HAS


@AudioRegistry.register()
def paired_pulse(sampling_rate: int,
                 channels: int,
                 duration: Tuple[Time, Time, Time],
                 methods: Tuple[str, str] = ("white_noise", "white_noise"),
                 volume: Tuple[float, float] = tuple([0.5, 1.0])
                 ) -> np.ndarray:
    # pre-pulse
    # noinspection PyProtectedMember
    pre_pulse = AudioRegistry._registry.get(methods[0])(sampling_rate, channels, duration[0], volume[0])

    # pulse gap
    # noinspection PyProtectedMember
    pulse_gap = AudioRegistry._registry.get("silence")(sampling_rate, channels, duration[1])

    # post-pulse
    # noinspection PyProtectedMember
    post_pulse = AudioRegistry._registry.get(methods[1])(sampling_rate, channels, duration[2], volume[1])

    samples = np.concatenate((pre_pulse, pulse_gap, post_pulse))

    return samples


@AudioRegistry.register()
def sawtooth(sampling_rate: int, channels: int, duration: Time, frequency: float) -> np.ndarray:
    duration = duration.seconds
    samples = int(sampling_rate * duration)
    time = np.arange(samples) / sampling_rate
    samples = 2 * (frequency * time - np.floor(frequency * time + 0.5))
    samples = samples.clip(-1, 1)
    if channels > 1:
        samples = np.tile(samples, (channels, 1)).T
    return samples


@AudioRegistry.register()
def silence(sampling_rate: int, channels: int, duration: Time) -> np.ndarray:
    duration = duration.seconds
    samples = int(sampling_rate * duration)
    return np.zeros((samples, channels))


@AudioRegistry.register()
def sine(sampling_rate: int, channels: int, duration: Time, frequency: float, volume = 1) -> np.ndarray:
    duration = duration.seconds
    samples = int(sampling_rate * duration)
    time = np.arange(samples) / sampling_rate
    samples = np.sin(2 * np.pi * frequency * time)
    if channels > 1:
        samples = np.tile(samples, (channels, 1)).T
    samples = rescale(samples, volume)
    return samples


@AudioRegistry.register()
def square(sampling_rate: int, channels: int, duration: Time, frequency: float) -> np.ndarray:
    duration = duration.seconds
    samples = int(sampling_rate * duration)
    time = np.arange(samples) / sampling_rate
    samples = np.sign(np.sin(2 * np.pi * frequency * time))
    if channels > 1:
        samples = np.tile(samples, (channels, 1)).T
    return samples


@AudioRegistry.register()
def triangle(sampling_rate: int, channels: int, duration: Time, frequency: float) -> np.ndarray:
    duration = duration.seconds
    samples = int(sampling_rate * duration)
    time = np.arange(samples) / sampling_rate
    samples = 2 * np.abs(2 * (time * frequency - np.floor(time * frequency + 0.5)))
    samples -= 1
    if channels > 1:
        samples = np.tile(samples, (channels, 1)).T
    return samples


@AudioRegistry.register()
def white_noise(sampling_rate: int, channels: int, duration: Time, volume: float = 1.0) -> np.ndarray:
    duration = duration.seconds
    samples = int(sampling_rate * duration)
    samples = np.random.randn(samples).flatten().T
    samples = samples.clip(-1, 1)
    if channels > 1:
        samples = np.tile(samples, (channels, 1)).T
    samples = rescale(samples, volume)
    return samples


def rescale(samples: np.ndarray, target_volume: float) -> np.ndarray:
    full_scale = [-1, 1]
    new_scale = [-target_volume, target_volume]
    return ((samples - full_scale[0]) * (new_scale[1] - new_scale[0])) / (full_scale[1] - full_scale[0]) + new_scale[0]
