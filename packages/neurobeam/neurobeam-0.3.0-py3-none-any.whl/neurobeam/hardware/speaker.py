from typing import Mapping, Optional
import warnings

from psychtoolbox.audio import Stream
from psychtoolbox.audio import verbosity as _set_verbosity
from scipy.interpolate import PchipInterpolator

from ..exceptions import SpeakerPropertyError, SpeakerSearchError, SpeakerVolumeWarning, SingletonError
from ..configs import HoistedConfig
from ..tools import HAS, find_devices
from ..timing import Milliseconds, Time, Seconds
from ..registries import Provider

"""
This speaker component inherits the Psychtoolbox audio package to interface with the speaker at low-latencies. Their 
implementation is quite good from my testing, so I don't have to reinvent the wheel write an interface or bindings to 
WASAPI. At least right now... It does mention it's experimental, so maybe I'll have to revisit this later and write my
own wrapper to WASAPI and make python bindings. package doesn't have any particular dependencies (just numpy) so not 
worried about dependency explosion. This is simply the speaker itself and is not intended to be used for stimuli 
generation and/or control. The speaker contains a LUT class that will ensure any stimuli are appropriately intense. 
The speaker is also capable of searching for itself during construction.
"""


_set_verbosity(0)


@Provider()
class Speaker(Stream):
    """
    This is a wrapper around the Psychtoolbox audio.Stream class alongside some complementary methods.
    It is used to connect to the speaker that will be used to delivery auditory stimuli.

    :param config: Config instance that contains a speaker sub-configuration.

    :param properties: A dictionary containing the properties of the speaker. If None, the speaker properties
    will be  located automatically.
    """

    # noinspection PyMissingConstructor
    def __init__(self,
                 config: Optional["HoistedConfig"] = None,
                 properties: Optional[Mapping[str, str]] = None,
                 speaker_id: str = "Digital",
                 lut: Optional[Mapping[str, str]] = None):
        """
        This is a wrapper around the Psychtoolbox audio.Stream class alongside some complementary methods.
        It is used to connect to the speaker that will be used to delivery auditory stimuli.

        :param config: The configuration that contains a hoisted speaker sub-configuration.
        :param properties: A dictionary containing the properties of the speaker. If None, the speaker properties
        will be  located automatically.
        :param speaker_id: The name of the speaker (used only if config is not provided).
        :param lut: A dictionary containing the look-up table for relating sound intensity to speaker volume (used only
            if config is not provided).

        """
        ################################################################################################################
        # REFERENCE CONFIGURATION
        ################################################################################################################
        self.config = config

        ################################################################################################################
        # GENERATE LUT TO RELATE SOUND INTENSITY TO SPEAKER VOLUME
        ################################################################################################################
        self.lut = config.lut if HAS(config) else lut
        self.lut = LUT(self.lut) if HAS(self.lut) else self.lut

        ################################################################################################################
        # FIND AND SET SPEAKER PROPERTIES. MAKE SURE WE ARE USING LOW-LATENCY API.
        ################################################################################################################
        self.speaker_id = config.speaker_id if HAS(config) else speaker_id

        self._properties = properties
        if properties is None:
            self._properties = self.search(name=self.speaker_id)
        self._validate()

        ################################################################################################################
        # INITIALIZE PSYCHTOOLBOX STREAM
        ################################################################################################################
        self.build()

    def __str__(self) -> str:
        return (f"{self.name}: "
                f"latency={self.latency.milliseconds} ms, "
                f"channels={self.channels}, "
                f"sampling rate={self.sampling_rate} Hz")

    @property
    def device_index(self) -> int:
        return int(self._properties.get("DeviceIndex"))

    @property
    def latency(self) -> "Time":
        return Seconds(self._properties.get("HighOutputLatency"))

    @property
    def name(self) -> str:
        return self._properties.get("DeviceName")

    @property
    def channels(self) -> int:
        return int(self._properties.get("NrOutputChannels"))

    @property
    def sampling_rate(self) -> int:
        return int(self._properties.get("DefaultSampleRate"))

    @property
    def start_time(self) -> float:
        return self.status.get("StartTime") if self.running else None

    @property
    def running(self) -> bool:
        return True if self.status.get("Active") == 1 else False

    @classmethod
    def search(cls, name: Optional[str] = None) -> Mapping:
        speakers = find_devices("speaker")
        for speaker_name, properties in speakers.items():
            if name is None:
                return properties
            elif name.lower() in speaker_name.lower():
                return properties
            else:  # pragma: no cover
                pass
        raise SpeakerSearchError(name, speakers)  # pragma: no cover

    def build(self) -> "Speaker":
        return Stream.__init__(self,
                               device_id=self.device_index,
                               latency_class=3,
                               freq=self.sampling_rate,
                               channels=self.channels,
                               mode=9)

    def start(self, *args, **kwargs):
        Stream.start(self, 0, 0, 0)

    def stop(self, *args, **kwargs):
        Stream.stop(self)

    def destroy(self):
        Stream.close(self)

    def __del__(self):
        self.destroy()

    def _validate(self):
        # make sure exists
        located_speakers = find_devices("speaker")

        if not any([speaker_name for speaker_name in located_speakers.keys()
                    if self.name in speaker_name]):  # pragma: no cover
            raise SpeakerSearchError(self.name, located_speakers)

        # make sure is WASAPI
        if self._properties.get("HostAudioAPIName") != "Windows WASAPI":  # pragma: no cover
            raise SpeakerPropertyError(self.name,
                                       "HostAudioAPIName",
                                       self._properties.get("HostAudioAPIName"),
                                       "Windows WASAPI")


class LUT(PchipInterpolator):
    """
    Look-up table relating sound intensity (decibels) to normalized speaker volume. This is used to ensure that the
    audio is appropriately intense. The LUT is interpolated using piecewise cubic hermite interpolating polynomial
    (PCHIP).

    """
    def __init__(self, lut_map: Mapping):
        self.lut_map = lut_map
        self.lut_map = {float(key): value for key, value in self.lut_map.items()}
        self._x = list(self.lut_map.keys())
        self._y = list(self.lut_map.values())
        self.rescale()
        super().__init__(self._x, self._y)

    def get(self, x: float) -> float:

        if x < min(self._x) or x > max(self._x):
            # return min or max volume if outside of range (whichever is closer)
            closer_to_max = abs(max(self._x) - x) < abs(min(self._x) - x)
            if closer_to_max:
                set_volume = 1.0
            else:
                set_volume = 0.0
            warnings.warn(SpeakerVolumeWarning(x, min(self._x), max(self._x), set_volume))
            return set_volume
        else:
            return super().__call__(x)

    def rescale(self):
        if not any([0 <= y <= 1 for y in self._y]):
            self._y = [y / max(self._y) for y in self._y]
