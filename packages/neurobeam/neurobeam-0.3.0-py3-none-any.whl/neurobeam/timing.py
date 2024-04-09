from ctypes import c_int64, byref, windll
from typing import Any, Union
import warnings

from .exceptions import TimeUnitParsingWarning


"""
Classes and functions related to timing and time representation.
"""


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// HIGH-PERFORMANCE TIMER
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


# this binding retrieves the current number of ticks from the windows performance counter
_k32_cnt = windll.Kernel32.QueryPerformanceCounter
# this binding retrieves the frequency of ticks collected by the windows performance counter
_k32_freq = windll.Kernel32.QueryPerformanceFrequency


def timer(units: int = 10**6) -> float:
    """
    Glue function for high-performance timer. Calls the windows performance counter and frequency through C-bindings.
    Note that these functions are not available on all platforms, and require that the processor's time-stamp counter
    is invariant across cores and threads, as well as invariant through boosting and changes in power-state. The vast
    majority of modern processors satisfy these requirements, and in the even they do not, modern windows versions
    (i.e., Windows 8/10/11) will automatically fal-lback to an invariant clock. This fal-lback clock is not as
    high-performance and high-resolution as the query performance counter, so you will end up with considerable larger
    intervals between timestamps and less precision in timing. While these effects are not relevant in most
    applications, it becomes very relevant in real-time systems like neurobeam.

    :param units: The units to return the time in. Default is microseconds.
    :returns: The relative time in the units of microseconds.

    .. seealso:: https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancefrequency

    .. seealso:: https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancecounter
    """
    count = c_int64()
    frequency = c_int64()

    _k32_cnt(byref(count))
    _k32_freq(byref(frequency))

    return count.value * units / frequency.value


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// TIME REPRESENTATION
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


class Time(int):
    """
    A class for representing time in various units. The class is a subclass of int, and can be used as such. The class
    will operate in units of microseconds, but by explicitly calling the properties, the time can be converted to
    the desired unit. Note that these conversions return floats, not an integer or a copy of the class.
    """
    _MICROS_PER_MILLISECOND = 10 ** 3
    _MICROS_PER_SECOND = 10 ** 6
    _MICROS_PER_MINUTE = 6 * 10 ** 7
    _MICROS_PER_HOUR = 36 * 10 ** 8

    def __new__(cls, time: int) -> "Time":
        return int.__new__(cls, time)

    @property
    def microseconds(self) -> float:
        """
        Converts the time to microseconds.

        :returns: The time in microseconds
        """
        return self

    @property
    def milliseconds(self) -> float:
        """
        Converts the time to milliseconds

        :returns: The time in milliseconds
        """
        return self / float(self._MICROS_PER_MILLISECOND)

    @property
    def seconds(self) -> float:
        """
        Converts the time to seconds

        :returns: The time in seconds
        """
        return self / float(self._MICROS_PER_SECOND)

    @property
    def minutes(self) -> float:
        """
        Converts the time to minutes

        :returns: The time in minutes
        """
        return self / float(self._MICROS_PER_MINUTE)

    @property
    def hours(self) -> float:
        """
        Converts the time to hours

        :returns: The time in hours
        """
        return self / float(self._MICROS_PER_HOUR)

    @staticmethod
    def __name__() -> str:
        return "Time"

    @classmethod
    def __toml_decode__(cls, data: Union[list, dict]) -> "Time":
        """
        Decodes a Time object from a serialized representation.

        :param data: The serialized representation of the Time object.
        :returns: An instance of Time
        """
        if isinstance(data, dict):
            value, units = data.get("value"), data.get("units")
        else:
            value, units = data
        if units in ("us", "µs", "microseconds"):
            return Microseconds(value)
        elif units in ("m", "minutes"):
            return Minutes(value)
        elif units in ("ms", "milliseconds"):
            return Milliseconds(value)
        elif units in ("s", "seconds"):
            return Seconds(value)
        elif units in ("h", "hours"):
            return Hours(value)
        else:
            warnings.warn(TimeUnitParsingWarning(units), stacklevel=2)
            return Microseconds(value)

    def __toml_encode__(self) -> list:
        """
        Encodes the Time object into a serializable representation.

        :returns: Serialized representation of the Time object.
        """
        name = self.__class__.__name__
        if name == "Time":
            return [self.microseconds, "microseconds"]
        else:
            return [getattr(self, name.lower()), name.lower()]

    def __copy__(self) -> "Time":
        """
        Returns a shallow copy of the Time object.
        """
        return Time(self.microseconds)

    def __deepcopy__(self, memo: dict) -> "Time":
        """
        Returns a deep copy of the Time object.
        """
        return Time(self.microseconds)

    def __instancecheck__(self, instance: Any) -> bool:
        """
        Checks if the instance is an instance of Time or any of its subclasses.

        :param instance: Existing instance to check.
        :returns: Whether the instance is an instance of Time or any of its subclasses.
        """
        if isinstance(instance, (Time, Microseconds, Milliseconds, Seconds, Minutes, Hours)):
            return True
        else:
            return super().__instancecheck__(instance)


class Microseconds(Time):
    """
    A class for representing time in microseconds. The class is a subclass of Time, and the value passed in the
    constructor argument will remain in units of microseconds when constructing an instance of
    :class:`Time <RF_PROBE.timing.Time>`.

    :param microseconds: The time in microseconds.
    :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

    .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
    """
    def __new__(cls, microseconds: float) -> "Time":
        """
        A class for representing time in microseconds. The class is a subclass of Time, and the value passed in the
        constructor argument will be converted from to microseconds to construct a Time instance.

        :param microseconds: The time in microseconds.
        :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

        .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
        """
        return Time.__new__(cls, int(microseconds))


class Milliseconds(Time):
    """
    A class for representing time in milliseconds. The class is a subclass of Time, and the value passed in the
    constructor argument will be converted from milliseconds to microseconds when constructing an instance of
    :class:`Time <RF_PROBE.timing.Time>`.

    :param milliseconds: The time in milliseconds.
    :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

    .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
    """
    def __new__(cls, milliseconds: float) -> "Time":
        """
        A class for representing time in milliseconds. The class is a subclass of Time, and the value passed in the
        constructor argument will be converted from milliseconds to microseconds when constructing an instance of
        :class:`Time <RF_PROBE.timing.Time>`.

        :param milliseconds: The time in milliseconds.
        :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

        .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
        """
        micros = int(milliseconds * Time._MICROS_PER_MILLISECOND)
        return Time.__new__(cls, micros)


class Seconds(Time):
    """
    A class for representing time in seconds. The class is a subclass of Time, and the value passed in the
    constructor argument will be converted from seconds to microseconds when constructing an instance of
    :class:`Time <RF_PROBE.timing.Time>`.

    :param seconds: The time in seconds
    :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

    .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
    """
    def __new__(cls, seconds: float) -> "Time":
        """
        A class for representing time in seconds. The class is a subclass of Time, and the value passed in the
        constructor argument will be converted from seconds to microseconds when constructing an instance of
        :class:`Time <RF_PROBE.timing.Time>`.

        :param seconds: The time in seconds
        :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

        .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
        """
        micros = int(seconds * Time._MICROS_PER_SECOND)
        return Time.__new__(cls, micros)


class Minutes(Time):
    """
    A class for representing time in minutes. The class is a subclass of Time, and the value passed in the
    constructor argument will be converted from minutes to microseconds when constructing an instance of
    :class:`Time <RF_PROBE.timing.Time>`.

    :param minutes: The time in minutes
    :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

    .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
    """
    def __new__(cls, minutes: float) -> "Time":
        """
        A class for representing time in minutes. The class is a subclass of Time, and the value passed in the
        constructor argument will be converted from minutes to microseconds when constructing an instance of
        :class:`Time <RF_PROBE.timing.Time>`.

        :param minutes: The time in minutes
        :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

        .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
        """
        micros = int(minutes * Time._MICROS_PER_MINUTE)
        return Time.__new__(cls, micros)


class Hours(Time):
    """
    A class for representing time in hours. The class is a subclass of Time, and the value passed in the
    constructor argument will be converted from hours to microseconds when constructing an instance of
    :class:`Time <RF_PROBE.timing.Time>`.

    :param hours: The time in hours
    :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

    .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
    """
    def __new__(cls, hours: float) -> "Time":
        """
        A class for representing time in hours. The class is a subclass of Time, and the value passed in the
        constructor argument will be converted from hours to microseconds when constructing an instance of
        :class:`Time <RF_PROBE.timing.Time>`.

        :param hours: The time in hours
        :returns: An instance of :class:`Time <RF_PROBE.timing.Time>` representing the time in microseconds.

        .. seealso:: :class:`Time <RF_PROBE.timing.Time>`
        """
        micros = int(hours * Time._MICROS_PER_HOUR)
        return Time.__new__(cls, micros)
