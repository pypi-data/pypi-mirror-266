from typing import Tuple, Callable, List, Any
from collections import deque
from pathlib import Path
from weakref import WeakValueDictionary
import warnings
from threading import RLock
from functools import partial

import numpy as np

from .exceptions import (OverloadedEventLogWarning, EmptyEventLogWarning, PathMismatchWarning,
                         RingSizeMismatchWarning, DataReorganizationWarning, DesynchronizedBuffersWarning)
from .timing import timer
from .tools import conditional_dispatch, EMPTY, HAS


"""
A collection of classes that simultaneously write data to file and maintain a ring buffer in memory for access by other
classes.
"""


class EventLog(deque):
    """
    Fast, fixed-size FIFO thread-safe ring buffer for event logs with concurrent writing to file. Implemented as
    doubly-linked list for O(1) append and pop operations. Implemented using a multiton design pattern allowing us to
    attach it to multiple threads and classes without explicit passing, but allows creation or selection of distinct
    instances using an instance cache. Calling add_data will add a timestamped event to the log. To avoid a ton of
    persistent entry-points or references to a single instance, you can use the wrap method to wrap the log across a
    function and remove the local instance of the log. Calling get-data will return the logged events with the
    rightmost element being the most recent.

    :param key: The key for instance registry
    :param path: The path that will have the key appended as a filename with extension .log
        default is the current working directory but not annotated as such
    :param ring_size: The number of events to store in the ring buffer log; default is 1 but not annotated as such
    :raises PathMismatchWarning: Raised if path does not match existing instance
    :raises RingSizeMismatchWarning: Raised if ring_size does not match existing instance
    :raises EmptyEventLogWarning: Raised if no event and action is provided to write data
    :raises OverloadedEventLogWarning: Raised if more than two arguments are provided to write data

    .. note :: This class adheres to the structural requirements of
        :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

    .. seealso:: https://en.wikipedia.org/wiki/Multiton_pattern
    """

    #: WeakValueDictionary: registry of instances
    __instance_registry = WeakValueDictionary()

    #: RLock: recursive mutex for thread safety
    __recursive_mutex = RLock()

    #: slots for instance attributes (faster attribute access)
    __slots__ = [
        "file",  #: file: file-handle
        "path",  #: Path: path to log file
        "_is_open"  #: bool: whether file is open
    ]

    def __new__(cls, key: str = "event_log", path: Path = None, ring_size: int = None) -> "EventLog":
        """
        Fast, fixed-size FIFO thread-safe ring buffer for event logs with concurrent writing to file. Implemented as
        doubly-linked list for O(1) append and pop operations. Implemented using a multiton design pattern allowing us
        to attach it to multiple threads and classes without explicit passing, but allows creation or selection of
        distinct instances using an instance cache. Calling add_data will add a timestamped event to the log. To avoid
        a ton of persistent entry-points or references to a single instance, you can use the wrap method to wrap the
        log across a function and remove the local instance of the log. Calling get-data will return the logged events
        with the rightmost element being the most recent.

        :param key: The key for instance registry
        :param path: The path that will have the key appended as a filename with extension .log
            default is the current working directory but not annotated as such
        :param ring_size: The number of events to store in the ring buffer log; default is 1 but not annotated as such
        :raises PathMismatchWarning: Raised if path does not match existing instance
        :raises RingSizeMismatchWarning: Raised if ring_size does not match existing instance
        :raises EmptyEventLogWarning: Raised if no event and action is provided to write data
        :raises OverloadedEventLogWarning: Raised if more than two arguments are provided to write data

        .. note :: This class adheres to the structural requirements of
            :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

        .. seealso:: https://en.wikipedia.org/wiki/Multiton_pattern
        """
        if EMPTY(cls.__instance_registry):
            return super().__new__(cls)
        elif key in cls.__instance_registry:
            instance = cls.__instance_registry.get(key)
            if HAS(path) and path != instance.path:
                warnings.warn(PathMismatchWarning(key, path, instance.path), stacklevel=2)
            if HAS(ring_size) and ring_size != len(instance):
                warnings.warn(RingSizeMismatchWarning(key, ring_size, len(instance)), stacklevel=2)
            return instance
        else:
            return super().__new__(cls)

    def __init__(self, key: str = "event_log", path: Path = None, ring_size: int = None):
        """
        Fast, fixed-size FIFO thread-safe ring buffer for event logs with concurrent writing to file. Implemented as
        doubly-linked list for O(1) append and pop operations. Implemented using a multiton design pattern allowing us
        to attach it to multiple threads and classes without explicit passing, but allows creation or selection of
        distinct instances using an instance cache. Calling add_data will add a timestamped event to the log. To avoid
        a ton of persistent entry-points or references to a single instance, you can use the wrap method to wrap the
        log across a function and remove the local instance of the log. Calling get-data will return the logged events
        with the rightmost element being the most recent.

        :param key: The key for instance registry
        :param path: The path that will have the key appended as a filename with extension .log
            default is the current working directory but not annotated as such
        :param ring_size: The number of events to store in the ring buffer log; default is 1 but not annotated as such
        :raises PathMismatchWarning: Raised if path does not match existing instance
        :raises RingSizeMismatchWarning: Raised if ring_size does not match existing instance
        :raises EmptyEventLogWarning: Raised if no event and action is provided to write data
        :raises OverloadedEventLogWarning: Raised if more than two arguments are provided to write data

        .. note :: This class adheres to the structural requirements of
            :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

        .. seealso:: https://en.wikipedia.org/wiki/Multiton_pattern
        """
        ################################################################################################################
        # ONLY INITIALIZE IF KEY NOT IN REGISTRY
        ################################################################################################################
        if key not in self.__instance_registry:
            if EMPTY(ring_size):
                ring_size = 1  # we provide a default this way so that we can warn the user so that we can
                # more simply identify if instance registry is called with a ring size mismatch
            super().__init__(list(range(ring_size)))
            if EMPTY(path):  # we provide a default this way so that we can warn the user we're reverting to default
                path = Path.cwd()
                warnings.warn(f"No path provided for {key}.log. Writing to {path}", stacklevel=2)
            # initialize instance attributes
            self.file = None
            self._is_open = False
            self.path = path.joinpath(f"{key}.log")
            self.open()
            self._initialize_data()
            self.__instance_registry[key] = self  # Add to registry only after successful initialization

    def __str__(self):
        return f"{self.__call__()}"

    @property
    def is_open(self) -> bool:
        """
        :Getter: Whether the log file is open.
        :Getter Type: :class:`bool`
        :Setter: This property is read-only.
        """
        return self._is_open

    def add_data(self, event: str, action: str) -> "EventLog":
        """
        Adds an event to the log with a timestamp in the form of "Timestamp\tEvent\tAction" with a tab delimiter. The
        timestamp is in microseconds with one decimal place. The timestamp is not directly related to any wall-clock,
        and will need to be compared relative to other timestamps to be useful. The event is the name of the
        object  (class, function, etc.) being logged, and the action is some description of the event. For example,
        "3504856465367.2\tButton\tPressed". This method is thread-safe.

        :param event: The name of the object or function being logged
        :param action: The action being logged

        .. warning:: The timestamp is not directly related to any wall-clock, and will need to be compared relative to
            other timestamps to be useful. The easiest way of doing this is to call a timestamp at the beginning of the
            experiment and use the timestamp as time zero.

        .. seealso:: :class:`Microseconds <RF_PROBE.timing.Microseconds>`
        """
        with self.__recursive_mutex:  # technically we make writing safe in _write data, but I'd prefer to only have
            # one thread calling add_data at a time. We'll use a reentrant lock
            data = f"{timer()}\t{event}\t{action}\n"  # format the data for writing
            self._write_data(data)
            self.pop()
            self.appendleft(data)

    def clear(self) -> "EventLog":
        """
        Clears the log's ring buffer and file handle
        """
        if self.is_open:
            self.close()
        self.file = None
        super().clear()

    def close(self) -> "EventLog":
        """
        Closes the log file.
        """
        with self.__recursive_mutex:
            if self.is_open:
                self.file.close()
                self._is_open = False

    def get_data(self) -> List[str]:
        """
        Retrieve the logged events the n-most recent logged events, where n is the size of the ring buffer
        (i.e., "ring_size").

        :returns: Logged events in the form of a list of strings where each string is in the form of
            "Timestamp\tEvent\tAction" with a tab delimiter. The rightmost element is the most recent.
        """
        return self  # this call is only here for consistency with other buffers

    def open(self) -> "EventLog":
        """
        Opens the log file.
        """
        if not self.is_open:
            self.file = open(self.path, "w")
            self._is_open = True

    def wrap(self, func: Callable) -> Callable:
        """
        Decorator method that wraps a function or method with the log_event method. This method allows one to log the
        calling of  an event without having to explicitly call the log_event method each time.

        :param func: The function to be decorated
        :returns: The new decorated function or method that can be used in place of the original one.
        """
        def wrapped_function(*args, **kwargs):  # noqa: ANN201
            if isinstance(func, partial):
                name = func.func.__name__
            else:
                name = func.__name__
            self.log_event(name, "called")
            return func(*args, **kwargs)
        return wrapped_function

    @conditional_dispatch
    def log_event(self, *args) -> "EventLog":
        """
        Dispatch method for logging events. This method is overloaded to handle different numbers of arguments. One
        could use a single method with "NULL" for default values of event and action, but the intention here is to
        provide a warning if the caller is not providing any information to the log rather than intentionally
        providing NULL.

        :param args: The first position argument is a string representing the event, and the second position argument
            is a string representing the action. If only one argument is provided, the action is set to "NULL".
        :raises EmptyEventLogWarning: Raised if no event or action is provided. In this case, the event and action are
            set to "NULL".
        :raises OverloadedEventLogWarning: Raised if more than two arguments have been provided. In this case, only the
            first two arguments will be used.
        """
        ...

    @log_event.register(lambda *args: len(args) == 1)
    def _(self, *args) -> "EventLog":
        """
        Method used when only the reference to the EventLog instance is provided. Sets both event and action to "NULL".

        :raises EmptyEventLogWarning:
        """
        self.add_data("NULL", "NULL")
        warnings.warn(EmptyEventLogWarning(), stacklevel=2)

    @log_event.register(lambda *args: len(args) == 2)
    def _(self, *args) -> "EventLog":
        """
        Method used when only the event is provided. Sets the action to "NULL".
        """
        self.add_data(args[0], "NULL")

    @log_event.register(lambda *args: len(args) == 3)
    def _(self, *args) -> "EventLog":
        """
        Method used when both the event and action are provided.
        """
        self.add_data(*args)

    @log_event.register(lambda *args: len(args) >= 4)
    def _(self, *args) -> "EventLog":
        """
        Method used when more than two arguments are provided. Only the first two arguments are used.

        :raises OverloadedEventLogWarning:
        """
        self.add_data(*args[:2])
        warnings.warn(OverloadedEventLogWarning(args), stacklevel=2)

    def _initialize_data(self) -> "EventLog":
        """
        Initializes the log's ring buffer with "Timestamp\tNULL\tNULL\n" for each element in the ring buffer.
        """
        for _ in range(len(self)):
            self.pop()
            self.appendleft(f"{timer()}\tNULL\tNULL\n")

    def _write_data(self, data: str) -> "EventLog":
        """
        Logs an event to the log file. This method is thread-safe.

        :param data: A string in the format of "Timestamp\tEvent\tAction" with a tab delimiter.
        """
        with self.__recursive_mutex:
            self.file.write(data)
            self.file.flush()


class RingBuffer(deque):
    """
    Fast, fixed-size FIFO thread-safe ring buffer for numerical data with concurrent writing to file. Implemented as
    doubly-linked list for O(1) append and pop operations.

    :param element_depth: The number of rows in each block of data
    :param element_length: The number of columns in each block of data
    :param ring_size: The number of blocks of data to store in the ring buffer
    :param path: The path to the file where the data will be written
    :param dtype: The data type of the data to be written
    :param do_reorganize: Whether to reorganize the data into a single numpy array after writing; default is True
    :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the number
     of elements required to reorganize the data. In this case, the raw data file will not be deleted.

    .. note :: This class adheres to the structural requirements of
        :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

    """
    __slots__ = [
        "pointer",
        # "block_shape", # Turns out that using slots prevents the use of cached_properties
        # "block_size", # I actually think it might be premature optimization to incorporate
        # "data_shape", # a property that calls a cached function, so commenting out for now
        # "data_size", # and leaving the properties as standard
        "element_depth",
        "element_length",
        "raw_path",
        "org_path",
        "data_type",
        "file",
        "do_reorganize",
        "_is_open"
    ]

    def __init__(self,
                 element_depth: int,
                 element_length: int,
                 ring_size: int,
                 path: Path,
                 dtype: np.dtype = np.float64,
                 do_reorganize: bool = True):
        """
        Fast, fixed-size FIFO thread-safe ring buffer for numerical data with concurrent writing to file. Implemented
        as doubly-linked list for O(1) append and pop operations.

        :param element_depth: The number of rows in each block of data
        :param element_length: The number of columns in each block of data
        :param ring_size: The number of blocks of data to store in the ring buffer
        :param path: The path to the file where the data will be written
        :param dtype: The data type of the data to be written
        :param do_reorganize: Whether to reorganize the data into a single numpy array after writing; default is True
        :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the
            number of elements required to reorganize the data. In this case, the raw data file will not be deleted

        .. note :: This class adheres to the structural requirements of
            :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`
        """
        super().__init__(list(range(ring_size)))
        self._is_open = False
        self.file = None
        self.do_reorganize = do_reorganize
        #: Path: path to for raw data
        if self.do_reorganize:
            self.raw_path = Path("".join([str(path), "_raw"]))
        else:
            self.raw_path = path
        #: Path: path for organized data
        self.org_path = path
        #: numpy.dtype: data type
        self.data_type = dtype
        #: int: index containing location for the most block of data to add to the ring  in the written data
        self.pointer = 0
        #: int: rows in data
        self.element_depth = element_depth
        #: int: columns in data
        self.element_length = element_length
        #: file-handle
        self.open()
        self._initialize_data()

    def __str__(self):
        return f"{self.__call__()}"

    @property
    def block_shape(self) -> Tuple[int, int]:
        """
        :Getter: The shape of each block of data in the ring buffer.
        :Getter Type: :class:`Tuple <tuple>`\\[:class:`int`, :class:`int`\\]
        :Setter: This property is read-only.
        """
        return self.element_depth, self.element_length

    @property
    def block_size(self) -> int:
        """
        :Getter: The size of each block of data in the ring buffer.
        :Getter Type: :class:`int`
        :Setter: This property is read-only.
        """
        return self.element_depth * self.element_length

    @property
    def data_shape(self) -> Tuple[int, int]:
        """
        :Getter: The shape of the data in the organized file.
        :Getter Type: :class:`Tuple <tuple>`\\[:class:`int`, :class:`int`\\]
        :Setter: This property is read-only.
        """
        return self.element_depth, self.element_length * self.pointer

    @property
    def data_size(self) -> int:
        """
        :Getter: The size of the data in the organized file.
        :Getter Type: :class:`int`
        :Setter: This property is read-only.
        """
        return self.element_depth * self.element_length * self.pointer

    @property
    def is_open(self) -> bool:
        """
        :Getter: Whether the associated file is open.
        :Getter Type: :class:`bool`
        :Setter: This property is read-only.
        """
        return self._is_open

    def add_data(self, data: np.ndarray) -> "RingBuffer":
        """
        Adds data to both the ring buffer and to the data file.

        :param data: The data to be added.
        """
        self._write_data(data)
        self.pop()
        self.appendleft(data)
        self.pointer += 1

    def clear(self) -> "RingBuffer":
        """
        Clears the ring buffer and file handle.
        """
        if self.is_open:
            self.close()
        self.file = None
        super().clear()

    def close(self) -> "RingBuffer":
        """
        Closes the file handle and reorganizes the data if the "do_reorganize" attribute is set to True.
        """
        if self.is_open:
            self.write_pointers()
            self.file.close()
            self._is_open = False
            if self.do_reorganize:
                self.reorganize()
                self._remove_raw()

    def open(self) -> "RingBuffer":
        """
        Opens the file handle.
        """
        if not self.is_open:
            self.file = open(self.raw_path, "wb", buffering=0)
            self._is_open = True

    def write_pointers(self) -> "RingBuffer":
        """
        Writes the pointer index to file for reshaping written data
        """
        with open(self.org_path.with_name(self.org_path.name + "_pointers"), "w") as f:
            f.write(str(self.pointer))

    def reorganize(self) -> "RingBuffer":
        """
        Reorganizes the data in the raw file into a single numpy array in the shape defined by the property
        :property:`RingBuffer.data_shape <RF_PROBE.data.RingBuffer.data_shape>`.
        """
        if self.pointer >= 1:
            raw_data = np.memmap(self.raw_path, dtype=self.data_type)
            self._validate_raw(raw_data)
            organized_data = np.memmap(self.org_path,
                                       mode="w+",
                                       shape=self.data_shape,
                                       dtype=self.data_type)
            # generate an index to grab each block of written data
            # org_idx = np.arange(self.data_shape[-1], dtype=np.int64)
            # org_idx = org_idx[0:-1:self.element_length].tolist() if self.element_length > 1 else org_idx.tolist()
            # org_idx.append(None)
            # raw_idx = np.arange(self.data_size, dtype=np.int64)
            # raw_idx = raw_idx[0:-1:self.block_size].tolist() if self.block_size > 1 else raw_idx.tolist()
            # raw_idx.append(None)
            org_idx = range(self.data_shape[-1])
            org_idx = list(org_idx[0:-1:self.element_length]) if self.element_length > 1 else list(org_idx)
            org_idx.append(None)
            raw_idx = range(self.data_size)
            raw_idx = list(raw_idx[0:-1:self.block_size]) if self.block_size > 1 else list(raw_idx)
            raw_idx.append(None)
            for block in range(self.pointer):
                organized_data[..., org_idx[block]:org_idx[block + 1]] \
                    = raw_data[raw_idx[block]:raw_idx[block + 1]].reshape(self.block_shape)
            organized_data.flush()

    def get_data(self) -> np.ndarray:
        """
        Retrieves the n-most recent blocks of data from the ring buffer, where n is the size of the ring buffer
        ("ring_size").

        :returns: The data from the ring buffer as a single numpy array where the rightmost column is the most recent.
        """
        return self.__call__()

    def _initialize_data(self) -> "RingBuffer":
        """
        Initializes the ring buffer with zeros.
        """
        if self.element_depth == 1 and self.element_length == 1:
            null_data = 0
        else:
            null_data = np.zeros(self.block_shape, dtype=self.data_type)
        for _ in range(len(self)):
            self.pop()
            self.appendleft(null_data)

    def _remove_raw(self) -> "RingBuffer":
        """
        Removes the raw data file if performing reorganization.
        """
        self.raw_path.unlink(missing_ok=True)

    def _validate_raw(self, raw_data: np.memmap) -> "RingBuffer":
        """
        Validates the raw data file to ensure that it contains the correct number of elements to be reorganized into
        into the shape defined by :property:`RingBuffer.data_shape <RF_PROBE.data.RingBuffer.data_shape>`.

        :param raw_data: The raw data to be validated.
        :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the
            number of elements required to reorganize the data. In this case, the raw data file will not be deleted.
        """
        try:
            assert len(raw_data) == self.data_size
            _ = raw_data.reshape(self.data_shape)
        except (AssertionError, ValueError):
            warnings.warn(DataReorganizationWarning(raw_data.size, self.data_shape), stacklevel=2)

    def _write_data(self, data: np.ndarray) -> "RingBuffer":
        """
        Writes data to the file handle.

        :param data: The data to be written to the file in the shape of
            :property:`RingBuffer.block_shape <RF_PROBE.data.RingBuffer.block_shape>`
        """
        self.file.write(data)
        # self.file.flush()

    def __call__(self) -> np.ndarray:
        """
        Stacks the data in the ring buffer into a single numpy array where the rightmost column is the most recent.
        """
        return np.hstack(self)


class TimestampedRingBuffer(RingBuffer):
    """
    Fast, fixed-size FIFO thread-safe ring buffer for numpy data with concurrent writing to file. Implemented as
    doubly-linked list for O(1) append and pop operations. A second file is creating with timestamps indicating the
    addition of each block of data to the ring buffer. The timestamps are in microseconds with one decimal place.

    :param element_depth: The number of rows in each block of data
    :param element_length: The number of columns in each block of data
    :param ring_size: The number of blocks of data to store in the ring buffer
    :param path: The path to the file where the data will be written
    :param dtype: The data type of the data to be written
    :param do_reorganize: Whether to reorganize the data into a single numpy array after writing; default is True
    :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the number
     of elements required to reorganize the data. In this case, the raw data file will not be deleted.

    .. note :: This class adheres to the structural requirements of
        :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

    .. seealso:: This class inherits from :class:`RingBuffer <RF_PROBE.data.RingBuffer>`

    .. seealso:: This class contains the :class:`Timestamping <RF_PROBE.data.Timestamping>` object for writing
        timestamps
    """
    __slots__ = [
        "pointer",
        # "block_shape", # Turns out that using slots prevents the use of cached_properties
        # "block_size", # I actually think it might be premature optimization to incorporate
        # "data_shape", # a property that calls a cached function, so commenting out for now
        # "data_size", # and leaving the properties as standard
        "element_depth",
        "element_length",
        "raw_path",
        "org_path",
        "data_type",
        "file",
        "timestamps",
        "do_reorganize",
        "_is_open"
    ]

    def __init__(self,
                 element_depth: int,
                 element_length: int,
                 ring_size: int,
                 path: Path,
                 dtype: np.dtype = np.float64,
                 do_reorganize: bool = True):
        """
        Fast, fixed-size FIFO thread-safe ring buffer for numpy data with concurrent writing to file. Implemented as
        doubly-linked list for O(1) append and pop operations. A second file is creating with timestamps indicating the
        addition of each block of data to the ring buffer. The timestamps are in microseconds with one decimal place.

        :param element_depth: The number of rows in each block of data
        :param element_length: The number of columns in each block of data
        :param ring_size: The number of blocks of data to store in the ring buffer
        :param path: The path to the file where the data will be written
        :param dtype: The data type of the data to be written
        :param do_reorganize: Whether to reorganize the data into a single numpy array after writing; default is True
        :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the
        number of elements required to reorganize the data. In this case, the raw data file will not be deleted.

        .. note :: This class adheres to the structural requirements of
            :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

        .. seealso:: This class inherits from :class:`RingBuffer <RF_PROBE.data.RingBuffer>`

        .. seealso:: This class contains the :class:`Timestamping <RF_PROBE.data.Timestamping>` object for writing
            timestamps
        """
        self.timestamps = Timestamping(path.with_name(path.name + "_timestamps"), ring_size=ring_size)
        super().__init__(element_depth, element_length, ring_size, path, dtype, do_reorganize)

    def add_data(self, data: np.ndarray) -> "TimestampedRingBuffer":
        """
        Adds data to both the ring buffer and to the data file, and adds a timestamp to the timestamp file.

        :param data: The data to be added.
        """
        super().add_data(data)
        self.timestamps.add_data()

    def clear(self) -> "RingBuffer":
        """
        Clears the ring buffer and file handle.
        """
        if self.is_open != self.timestamps.is_open:
            warnings.warn(DesynchronizedBuffersWarning((self.__class__.__name__,
                                                        self.timestamps.__class__.__name__)),
                          stacklevel=2)
        if self.is_open:
            self.close()
            self.timestamps.close()
        self.file = None
        self.timestamps.clear()
        super().clear()

    def close(self) -> "TimestampedRingBuffer":
        """
        Closes the file handle for both the timestamps and data, and reorganizes the data if the "do_reorganize"
        attribute is set to True.
        """
        if self.is_open != self.timestamps.is_open:
            warnings.warn(DesynchronizedBuffersWarning((self.__class__.__name__,
                                                        self.timestamps.__class__.__name__)),
                          stacklevel=2)
        if self.is_open:
            self.timestamps.close()
            super().close()

    def open(self) -> "TimestampedRingBuffer":
        """
        Opens the file handle for both the timestamps and data.
        """
        if self.is_open != self.timestamps.is_open:
            warnings.warn(DesynchronizedBuffersWarning((self.__class__.__name__,
                                                        self.timestamps.__class__.__name__)),
                          stacklevel=2)
        if not self.is_open:
            self.timestamps.open()
            super().open()

    def get_data(self) -> np.ndarray:
        """
        Retrieves the n-most recent blocks of data from the ring buffer, where n is the size of the ring buffer
        ("ring_size").

        :returns: The data from the ring buffer as a single numpy array where the rightmost column is the most recent.
        """
        return self.__call__()

    def get_timestamps(self) -> np.ndarray:
        """
        Retrieves the n-most recent timestamps from the ring buffer, where n is the size of the ring buffer
        ("ring_size").

        :returns: The timestamps from the ring buffer as a single numpy array where the rightmost column is the
            most recent.
        """
        return self.timestamps.get_data()


class Timestamping(RingBuffer):
    """
    Fast, fixed-size FIFO thread-safe ring buffer for timestamps with concurrent writing to file. Implemented as
    doubly-linked list for O(1) append and pop operations. The timestamps are in microseconds with one decimal place.

    :param path: The path to the file where the data will be written
    :param ring_size: The number of timestamps to store in the ring buffer; default is 1
    :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the number
        of elements required to reorganize the data. In this case, the raw data file will not be deleted.

    .. note :: This class adheres to the structural requirements of
        :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

    .. seealso:: This class inherits from :class:`RingBuffer <RF_PROBE.data.RingBuffer>`

    .. seealso:: This class utilizes the :function:`timer <RF_PROBE.timing.timer>` function for collecting
        timestamps.
    """
    __slots__ = [
        "pointer",
        # "block_shape", # Turns out that using slots prevents the use of cached_properties
        # "block_size", # I actually think it might be premature optimization to incorporate
        # "data_shape", # a property that calls a cached function, so commenting out for now
        # "data_size", # and leaving the properties as standard
        "element_depth",
        "element_length",
        "raw_path",
        "org_path",
        "data_type",
        "file",
        "do_reorganize",
        "_is_open"
    ]

    def __init__(self, path: Path, ring_size: int = 1):
        """
        Fast, fixed-size FIFO thread-safe ring buffer for timestamps with concurrent writing to file. Implemented as
        doubly-linked list for O(1) append and pop operations. The timestamps are in microseconds with one decimal
        place.

        :param path: The path to the file where the data will be written
        :param ring_size: The number of timestamps to store in the ring buffer; default is 1
        :raises DataReorganizationWarning: Raised if the number of elements in the raw data file does not match the
        number of elements required to reorganize the data. In this case, the raw data file will not be deleted.

        .. note :: This class adheres to the structural requirements of
            :class:`DataBuffer <RF_PROBE.extensions.DataBuffer>`

        .. seealso:: This class inherits from :class:`RingBuffer <RF_PROBE.data.RingBuffer>`

        .. seealso:: This class utilizes the :function:`timer <RF_PROBE.timing.timer>` function for collecting
            timestamps.
        """
        super().__init__(1, 1, ring_size, path, np.float64, False)

    def add_data(self, data: Any = None) -> "Timestamping":  # noqa: U100
        """
        Adds a timestamp to the file.

        :param data: This argument is here for compatibility with the RingBuffer class, but is not used.

        ..warning:: The data argument is not used in this method and only exists for compatibility with the parent
            :class:`RingBuffer <RF_PROBE.data.RingBuffer>` class.

        ..seealso:: :class:`RingBuffer <RF_PROBE.data.RingBuffer>`
        """
        super().add_data(np.asarray(timer()))
