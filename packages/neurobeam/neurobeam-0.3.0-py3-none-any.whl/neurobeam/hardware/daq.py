from __future__ import annotations
from typing import Tuple, Any, Mapping, Union, List
import warnings
from abc import abstractmethod, ABC

import nidaqmx
import nidaqmx.stream_readers
import nidaqmx.stream_writers
import numpy as np
from frozendict import frozendict

from ..exceptions import SingletonError
from ..configs import Config, HoistedConfig
from ..data import RingBuffer, TimestampedRingBuffer
from ..tools import HAS
from ..registries import CallbackRegistry, Provider
from ..requests import CallbackRequest


"""
Components and sub-components for National Instruments Data Acquisition Devices.
"""


"""
Abstract Components
"""


@Provider()
class StreamingComponent:
    name = "Streaming Component"

    def __init__(self,
                 config: Config):
        self.device_id = config.device_id
        ################################################################################################################
        # PRE-ALLOCATE
        ################################################################################################################
        # pre-allocated
        #: int: buffer size for each channel
        self.buffer_size = None
        #: np.dtype: dtype for collected data
        self.data_type = None
        #: np.ndarray: buffer object of size channels x buffer size
        self.data = None

        ################################################################################################################
        # INITIALIZATION FROM CONFIG
        ################################################################################################################
        #: int: sampling rate for all DAQ streams (Hz)
        self.sampling_frequency = config.sampling_frequency
        #: int: buffer rate for daq
        self.buffer_frequency = config.buffer_frequency
        #: float: timeout for DAQ interaction (s)
        self.timeout = config.timeout
        #: frozendict: channel index hashmap
        self.channel_index = frozendict()
        #: frozendict: dictionary of individual channel strings
        self.channel_ids = frozendict()
        #: int: number of channels
        self.num_channels = 0
        #: str: flattened channel string for DAQ
        self.channel_str = ""
        #: frozendict: channel - buffer row mapping
        self.buffer_index = frozendict()
        # ingest channel information
        self.retrieve_channel_info(config)
        self.output_file = (
            config.save_location.joinpath(config.file_header + self.name.lower().replace(" ", "_")))
        self.ring_buffer = None
        #: nidaqmx.Task: streaming object & is really only called in subclass's init
        self.streamer = None  # self.generate_streamer
        # #: nidaqmx.stream_readers or nidaqmx.stream_writers: stream processor object, called subclass init
        self.stream_processor = None  # self.generate_processor

    def __str__(self):
        return self.name

#    def find_request_callbacks(self) -> StreamingComponent:
#        self.request_callbacks = [self.callbacks.get(key) for key in self.callbacks if "request" in key]
#
#    def find_update_callbacks(self) -> StreamingComponent:
#        self.update_callbacks = [(self.callbacks.get("".join([key, "_update"])), value)
#                                 for key, value in self.buffer_index.items()]

    @abstractmethod
    def generate_processor(self) -> StreamingComponent:
        ...

    @abstractmethod
    def generate_streamer(self) -> StreamingComponent:
        ...

    @abstractmethod
    def generate_ni_buffer(self, config: "Config"):
        ...

    def generate_ring_buffer(self) -> StreamingComponent:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.ring_buffer = TimestampedRingBuffer(element_depth=self.num_channels,
                                                     element_length=self.buffer_size,
                                                     ring_size=self.buffer_frequency * 10,
                                                     path=self.output_file,
                                                     dtype=self.data_type)

    @abstractmethod
    def retrieve_channel_info(self, config: Config) -> StreamingComponent:
        """
        Retrieves dictionary of channel index hashmap, channel string ids, number of channels,
        and flattened channel string
        """
        pass

    @abstractmethod
    def start_component(self) -> StreamingComponent:
        ...

    def stream_request(self) -> int:
        """
        Request in-place update of a data stream

        :return: 0
        :rtype: int
        """
        # READ DATA
        self._stream_callback_read()
        # UPDATE RING BUFFER
        self.ring_buffer.add_data(self.data)
        # USE NEW DATA FOR CALLBACKS
        self._stream_callback_calls(self.ring_buffer.get_data())
        return 0

    @abstractmethod
    def _stream_callback_read(self):
        ...

    @abstractmethod
    def _stream_callback_calls(self, data):
        ...

    def _stream_callback(self, task_handle: str, every_n_samples_event_type: Any, number_of_samples: int,
                         callback_data: np.ndarray) -> int:
        """
        In place update of a data stream

        :param task_handle: task handle for nidaqmx task
        :type task_handle: str
        :param every_n_samples_event_type: specifies the event is an every_n_samples_event
        :type every_n_samples_event_type: Any
        :param number_of_samples: samples to collect before callback
        :type number_of_samples: int
        :param callback_data: reference to the data buffer
        :type callback_data: np.ndarray
        :return: 0
        :rtype: int
        """
        # READ DATA
        self._stream_callback_read()
        # UPDATE RING BUFFER
        self.ring_buffer.add_data(self.data)
        # USE NEW DATA FOR CALLBACKS
        self._stream_callback_calls(self.ring_buffer.get_data())
        return 0

    def destroy(self):
        try:
            # Make sure it's actually a defined task and not the base component or empty streamer
            assert self.streamer
        except (AttributeError, AssertionError):
            pass  # No task handle proceed
        else:
            self.streamer.stop()
            self.streamer.close()

    def __del__(self):
        if HAS(self.streamer):
            delattr(self, "streamer")


@Provider()
class OnDemandComponent(nidaqmx.Task):

    #: str: name of component
    name = "On-Demand Component"

    # noinspection PyMissingConstructor
    def __init__(self, config: Config):
        self.device_id = config.device_id
        nidaqmx.Task.__init__(self, self.name)

        ################################################################################################################
        # PRE-ALLOCATE
        ################################################################################################################
        #: int: buffer size for each channel
        self.buffer_size = None
        #: np.dtype: dtype for collected data
        self.data_type = None
        #: np.ndarray: buffer object of size channels x buffer size
        self.data = None

        ################################################################################################################
        # INITIALIZATION FROM CONFIG
        ################################################################################################################
        #: int: sampling rate for all DAQ streams (Hz)
        self.sampling_rate = config.sampling_frequency
        #: float: timeout for DAQ interaction (s)
        self.timeout = config.timeout
        #: frozendict: channel index hashmap
        self.channel_index = frozendict({})
        #: frozendict: channel voltage hashmap
        self.channel_limits = frozendict({})
        #: dict: dictionary of individual channel strings
        self.channel_ids = {}
        #: Tuple[str, ...]: key ids of channels
        self.cids = None
        #: int: number of channels
        self.num_channels = 0
        #: str: flattened channel string for DAQ
        self.channel_str = ""
        #: frozendict: channel - buffer row mapping
        self.buffer_index = frozendict({})
        # ingest channel information
        self.retrieve_channel_info(config)

    def __str__(self):
        return self.name

    @abstractmethod
    def command(self, values: Union[float, np.ndarray]) -> "OnDemandComponent":
        ...

    @abstractmethod
    def generate_ni_buffer(self, config):
        ...

    @abstractmethod
    def retrieve_channel_info(self, config: Config) -> "OnDemandComponent":
        """
        Retrieves dictionary of channel index hashmap, channel limits, channel string ids, number of channels,
        and flattened channel string
        """
        ...

    @abstractmethod
    def send(self):
        ...

    @abstractmethod
    def start_component(self) -> OnDemandComponent:
        ...

    def destroy(self):
        try:
            # Make sure it's actually a defined task and not the base component or empty streamer
            assert self._handle
        except (AttributeError, AssertionError):
            pass  # No task handle proceed
        else:
            self.stop()
            self.close()


"""
Analog Input
"""


class AnalogMultiInputStream(StreamingComponent):
    """
    Object for streaming analog inputs
    """
    #: str: name of analog input object
    name = "Analog Input Stream"

    def __init__(self, config: Config):
        self.timestamps = None
        self.voltage_range = config.analog_input_range

        super().__init__(config)
        self.generate_ni_buffer(config)
        self.generate_ring_buffer()
        self.generate_streamer()
        self.generate_processor()

        # make sure this is multi-stream
        if self.num_channels <= 1:
            raise ValueError(f"AnalogMultiInputStream requires multiple channels: {self.num_channels=}")

        # set callbacks
        self.digital_input_request = CallbackRequest(requesting_instance=self, key="digital_input_request")

    def retrieve_channel_info(self, config: Config) -> AnalogMultiInputStream:
        """
        Retrieves dictionary of channel index hashmap, channel string ids, number of channels,
        and flattened channel string
        """
        self.channel_index = config.analog_input_index
        self.channel_ids = config.analog_input_channels
        self.num_channels = config.num_analog_input_channels
        self.channel_str = config.flattened_analog_inputs
        self.buffer_index = frozendict(
            {pair[1]: pair[0] for pair in enumerate(config.analog_input_index.keys())})

    def generate_streamer(self) -> AnalogMultiInputStream:
        self.streamer = AnalogAcquisition(self.name, self.channel_str, self.voltage_range,
                                          self.sampling_frequency)

    def generate_processor(self) -> AnalogMultiInputStream:
        self.stream_processor = AnalogMultiStreamReader(self.streamer)

    def generate_ni_buffer(self, config: "Config"):
        self.buffer_size = config.analog_buffer_size
        self.data_type = np.float64
        self.data = np.full((self.num_channels, self.buffer_size), 0, dtype=self.data_type)

    def start_component(self) -> AnalogMultiInputStream:
        """
        Sets callbacks for every N samples and then starts data acquisition

        :rtype: Self
        """
        self.streamer.register_every_n_samples_acquired_into_buffer_event(
            self.buffer_size, callback_method=self._stream_callback)
        self.streamer.start()

    def _stream_callback_read(self) -> int:
        """
        In place update of a data stream

        :param task_handle: task handle for nidaqmx task
        :type task_handle: str
        :param every_n_samples_event_type: specifies the event is an every_n_samples_event
        :type every_n_samples_event_type: Any
        :param number_of_samples: samples to collect before callback
        :type number_of_samples: int
        :param callback_data: reference to the data buffer
        :type callback_data: np.ndarray
        :return: 0
        :rtype: int
        """
        self.stream_processor.read_many_sample(data=self.data, number_of_samples_per_channel=self.buffer_size,
                                               timeout=self.timeout)

    def _stream_callback_calls(self, data):

        if self.digital_input_request:
            self.digital_input_request()


# noinspection PyUnresolvedReferences
class AnalogAcquisition(nidaqmx.Task):
    """
    Analog Input Source (Streamer)
    """

    def __init__(self, name: str, flattened_channel_str: str, voltage_range: Tuple[float, float], sampling_rate: int):
        # call superclass
        nidaqmx.Task.__init__(self, name)
        # generate channels
        self.ai_channels.add_ai_voltage_chan(flattened_channel_str, name,
                                             terminal_config=nidaqmx.constants.TerminalConfiguration.RSE,
                                             min_val=voltage_range[0], max_val=voltage_range[1])
        # establish timing
        self.timing.cfg_samp_clk_timing(sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)


class AnalogMultiStreamReader(nidaqmx.stream_readers.AnalogMultiChannelReader):
    """
    Reader of a multi-channel analog data stream

    """
    def __init__(self, analog: AnalogAcquisition):
        super().__init__(analog.in_stream)


class AnalogSingleStreamReader(nidaqmx.stream_readers.AnalogSingleChannelReader):
    """
    Reader of a single-channel analog data stream

    """
    def __init__(self, analog: AnalogAcquisition):
        super().__init__(analog.in_stream)


"""
Analog Output
"""


class AnalogWriter(OnDemandComponent):
    """
    Instance Factory for writing analog

    """
    #: str: name of component
    name = "Analog Output"

    def __init__(self, config: Config):

        # I AM TASK
        # nidaqmx.Task.__init__(self, self.name)

        super().__init__(config)
        self.generate_ni_buffer(config)

        # get general voltage range
        self.voltage_range = (min(min(config.analog_output_range.values())),
                              max(max(config.analog_output_range.values())))

        #: nidaqmx._task_modules.ao_channel_collection.AOChannelCollection: analog output channel object
        self.ao_channels.add_ao_voltage_chan(self.channel_str, self.name, *self.voltage_range)

        # set output command to voltage min
        for cid in self.cids:
            self.data[config.analog_output_index.get(cid), :] = config.analog_output_range.get(cid)[0]

    def command(self, values: Union[float, np.ndarray]) -> "AnalogWriter":
        self.data[..., :] = values

    def generate_ni_buffer(self, config):
        self.buffer_size = config.analog_buffer_size
        self.data_type = np.float64
        self.data = np.full((self.num_channels, self.buffer_size), 0.0, dtype=self.data_type)

    def retrieve_channel_info(self, config: Config) -> "AnalogWriter":
        """
        Retrieves dictionary of channel index hashmap, channel string ids, number of channels,
        and flattened channel string
        """
        self.channel_index = config.analog_output_index
        self.channel_ids = config.analog_output_channels
        self.num_channels = config.num_analog_output_channels
        self.channel_str = config.flattened_analog_outputs
        self.cids = config.analog_output_cids
        self.channel_limits = config.analog_output_range
        self.buffer_index = config.analog_output_index

    def send(self):
        self.write(data=self.data, auto_start=True, timeout=self.timeout)

    def start_component(self) -> "AnalogWriter":
        self.start()


"""
Digital Input
"""


class DigitalMultiInputStream(StreamingComponent):
    """
    Object for streaming digital inputs
    """
    #: str: name of digital input object
    name = "Digital Input Stream"

    def __init__(self, config: Config):
        super().__init__(config)
        self.generate_ni_buffer(config)
        self.generate_ring_buffer()
        self.generate_streamer()
        self.generate_processor()

        # make sure this is multi-stream
        if self.num_channels <= 1:
            raise ValueError(f"DigitalMultiInputStream requires multiple channels: {self.num_channels=}")
        return

    @CallbackRegistry.register()
    def digital_input_request(self):
        self.stream_request()

    def retrieve_channel_info(self, config: Config) -> DigitalMultiInputStream:
        """
        Retrieves dictionary of channel index hashmap, channel string ids, number of channels,
        and flattened channel string
        """
        self.channel_index = config.digital_input_index
        self.channel_ids = config.digital_input_channels
        self.num_channels = config.num_digital_input_channels
        self.channel_str = config.flattened_digital_inputs
        self.buffer_index = frozendict(
            {pair[1]: pair[0] for pair in enumerate(config.digital_input_index.keys())})

    def start_component(self) -> DigitalMultiInputStream:
        """
        starts data acquisition

        """
        self.streamer.start()

    def generate_streamer(self) -> DigitalMultiInputStream:
        self.streamer = DigitalAcquisition(self.name, self.channel_str, self.sampling_frequency, self.buffer_size,
                                           self.timeout)

    def generate_processor(self) -> DigitalMultiInputStream:
        self.stream_processor = DigitalMultiStreamReader(self.streamer)

    def generate_ni_buffer(self, config: "Config"):
        self.buffer_size = config.digital_buffer_size
        self.data_type = np.uint8
        self.data = np.full((self.num_channels, self.buffer_size), 0, dtype=self.data_type)

    def _stream_callback_read(self):
        self.stream_processor.read_many_sample_port_byte(data=self.data,
                                                         number_of_samples_per_channel=self.buffer_size,
                                                         timeout=self.timeout)

    def _stream_callback_calls(self, data):
        # callbacks for updating data
        #for callback, index in self.update_callbacks:
        #    callback([self.buffer_sample_index, data[index, :]])
        pass


class DigitalAcquisition(nidaqmx.Task):
    """
    Digital Input Source

    """

    def __init__(self, name: str, flattened_channel_str: str, sampling_rate: str, buffer_size: int, timeout: int):
        self.sampling_rate = sampling_rate
        self.buffer_size = buffer_size
        self.timeout = timeout
        nidaqmx.Task.__init__(self, name)
        self.di_channels.add_di_chan(flattened_channel_str, name,
                                     nidaqmx.constants.LineGrouping.CHAN_PER_LINE)


class DigitalMultiStreamReader(nidaqmx.stream_readers.DigitalMultiChannelReader):
    """
    Reader of a multi-channel digital data stream

    """
    def __init__(self, digital: DigitalAcquisition):
        super().__init__(digital.in_stream)


class DigitalSingleStreamReader(nidaqmx.stream_readers.DigitalSingleChannelReader):
    """
    Reader of a single-channel digital data stream

    """
    def __init__(self, digital: DigitalAcquisition):
        super().__init__(digital.in_stream)


"""
Digital Output
"""


class DigitalMultiOutputStream(StreamingComponent):
    #: str: name of digital output object
    name = "Digital MultiOutput Stream"

    def __init__(self, config: Config):
        super().__init__(config)
        self.generate_ni_buffer(config)
        self.generate_streamer()
        self.generate_processor()

        # make sure this is multi-stream
        if self.num_channels <= 1:
            raise ValueError(f"DigitalMultiOutputStream requires multiple channels: {self.num_channels=}")
        return

    def retrieve_channel_info(self, config: Config) -> DigitalMultiOutputStream:
        """
        Retrieves dictionary of channel index hashmap, channel string ids, number of channels,
        and flattened channel string
        """
        self.channel_index = config.digital_output_index
        self.channel_ids = config.digital_output_channels
        self.num_channels = config.num_digital_output_channels
        self.channel_str = config.flattened_digital_outputs
        self.buffer_index = frozendict(
            {pair[1]: pair[0] for pair in enumerate(config.digital_output_index.keys())})

    def generate_streamer(self) -> DigitalMultiOutputStream:
        self.streamer = DigitalWriter(self.name,
                                      self.channel_str,
                                      self.sampling_frequency,
                                      self.buffer_size,
                                      self.timeout)

    def generate_processor(self) -> DigitalMultiOutputStream:
        self.stream_processor = DigitalMultiStreamWriter(self.streamer)

    def generate_ni_buffer(self, config: "Config"):
        self.buffer_size = 1
        self.data_type = np.bool_
        self.data = np.full((self.num_channels, self.buffer_size), False, dtype=self.data_type)

    def start_component(self) -> DigitalMultiOutputStream:
        self.streamer.start()
        self.initialize()

    def stop(self):
        self.streamer.stop()

    def initialize(self) -> DigitalMultiOutputStream:
        # format_data(self.data, self.num_channels)
        #self.data[0] = 1
        self.streamer.write(self.data, auto_start=True, timeout=self.timeout)
        # self.stream_processor.write_many_sample_port_byte(self.data, self.timeout)

    @CallbackRegistry.register(alias="digital_output_write")
    def stream_request(self) -> int:
        self.streamer.write(self.data, auto_start=True, timeout=self.timeout)
        return 0

    def _stream_callback_read(self):
        pass

    def _stream_callback_calls(self, data):
        pass


class DigitalWriter(nidaqmx.Task):
    """
    Digital Output Source

    """
    def __init__(self, name: str, flattened_channel_str: str, sampling_rate: str, buffer_size: int, timeout: int):
        self.sampling_rate = sampling_rate
        self.buffer_size = buffer_size
        self.timeout = timeout
        nidaqmx.Task.__init__(self, name)
        self.do_channels.add_do_chan(flattened_channel_str, name,
                                     nidaqmx.constants.LineGrouping.CHAN_PER_LINE)


class DigitalMultiStreamWriter(nidaqmx.stream_writers.DigitalMultiChannelWriter):
    """
    Writer of a multi-channel digital data stream

    """
    def __init__(self, digital: DigitalWriter):
        super().__init__(digital.out_stream)


class DigitalSingleStreamWriter(nidaqmx.stream_writers.DigitalSingleChannelWriter):
    """
    Writer of a single-channel digital data stream

    """
    def __init__(self, digital: DigitalWriter):
        super().__init__(digital.out_stream)


"""
Complete DAQ Object
"""


@Provider()
class DAQ:
    """
    Container component for national instruments data acquisition. Presently, analog_input loops on the main thread but
    only once for every N samples. The actual collection is abstracted through C++ and is hardware-timed. Depending on
    the model of National Instruments DAQ, the digital input might be software or hardware-timed. Hence, the
    analog_input callback calls digital_input to collect a smaller set of samples. Again, the acquisition is abstracted
    through C++. However, the timing is not guaranteed and may contain small amounts of jitter. Therefore, it's best to
    consider the effective acquisition rate for the digital input to be the analog_input's buffer rate. The output
    components analog_output and digital_output are considered "on-demand" components. Their values change only when
    directed and otherwise hold the latest commanded values. Interfaces can be created to facilitate manipulating these
    values in a more meaningful syntax: for example, the linear actuator interface can move the motor in terms of
    physical units instead of voltage. The adapters are dynamically constructed instance attributes and long-term I
    should think about lifting those up to the main level of the controller container. In this way, it could be
    possible to create adapters for input that simply reference the respective channel and might facilitate collect
    by the GUI--as well as hide the actual hardware implementations. Something to think about...

    :param config: The neurobeam configuration
    :param idx: The index of the DAQ in the configuration's component
    """

    def __init__(self, config: Union["Config", "HoistedConfig"]) -> "DAQ":
        ################################################################################################################
        # REFERENCE CONFIG
        ################################################################################################################
        self.config = config

        ################################################################################################################
        # PRE-ALLOCATE
        ################################################################################################################
        self.analog_input = None
        self.analog_output = None
        self.digital_input = None
        self.digital_output = None
        self._running = False

        ################################################################################################################
        # BUILD COMPONENTS
        ################################################################################################################
        self.build()

    def __str__(self) -> str:
        return f"National Instruments DAQ: {self.config.device_id}"

    def __name__(self) -> str:
        return self.config.device_id

    @property
    def running(self) -> bool:
        """
        :Getter: Returns the running status of the DAQ
        :Getter Type: :class:`bool`
        :Setter: This property is read-only
        """
        return self._running

    @property
    def subcomponents(self) \
            -> Tuple[AnalogMultiInputStream, AnalogWriter, DigitalMultiInputStream, DigitalMultiOutputStream]:

        return [getattr(self, subcomponent) for subcomponent in ("analog_input",
                                                                 "analog_output",
                                                                 "digital_input",
                                                                 "digital_output")]

    @property
    def readers(self) -> Tuple[AnalogMultiInputStream, DigitalMultiInputStream]:
        return [getattr(self, subcomponent) for subcomponent in ("analog_input", "digital_input")]

    @property
    def writers(self) -> Tuple[AnalogWriter, DigitalMultiOutputStream]:
        return [getattr(self, subcomponent) for subcomponent in ("analog_output", "digital_output")]

    def build(self) -> "DAQ":
        self.analog_input = AnalogMultiInputStream(self.config) \
            if self.analog_input is None else self.analog_input
        self.analog_output = AnalogWriter(self.config) \
            if self.analog_output is None else self.analog_output
        self.digital_input = DigitalMultiInputStream(self.config) \
            if self.digital_input is None else self.digital_input
        self.digital_output = DigitalMultiOutputStream(self.config) \
            if self.digital_output is None else self.digital_output

    def start(self) -> "DAQ":
        if not self.running:
            for subcomponent in self.subcomponents:
                subcomponent.start_component()
            self._running = True

    def stop(self) -> "DAQ":
        if self.running:
            # Stop readers first since they might potentially call the writers.
            for subcomponent in self.readers:
                subcomponent.streamer.stop()
            for subcomponent in self.writers:
                subcomponent.stop()
            # Make sure to close and save the ring buffers
            for subcomponent in self.readers:
                subcomponent.ring_buffer.close()
            self._running = False

    def destroy(self):
        if self.running:
            self.stop()
        # Destroy components
        for subcomponent in self.subcomponents:
            if subcomponent:
                subcomponent.destroy()

    def __del__(self):
        self.destroy()
