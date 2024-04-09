import pytest

from neurobeam.data import EventLog, RingBuffer, TimestampedRingBuffer, Timestamping
from neurobeam.exceptions import (DataReorganizationWarning, PathMismatchWarning, RingSizeMismatchWarning,
                                  EmptyEventLogWarning, OverloadedEventLogWarning)
import numpy as np


def test_event_log(tmp_path):
    log = EventLog("event_log", path=tmp_path, ring_size=5)
    for _ in range(100):
        log.log_event("TEST", "LOGGING")
    log2 = EventLog(path=tmp_path, ring_size=5)
    log2.log_event("TEST", "LOGGING")
    log.close()
    log2.close()
    del log
    del log2

    # test warnings
    with pytest.warns(PathMismatchWarning):
        log = EventLog("event_log", path=tmp_path, ring_size=5)
        log2 = EventLog("event_log", path=tmp_path.with_name("beans"))
        del log
        del log2
    with pytest.warns(RingSizeMismatchWarning):
        log = EventLog("event_log", path=tmp_path, ring_size=5)
        log2 = EventLog("event_log", path=tmp_path, ring_size=10)
        del log
        del log2
    with pytest.warns(EmptyEventLogWarning):
        log = EventLog("event_log", path=tmp_path)
        log.log_event()
        del log
    with pytest.warns(OverloadedEventLogWarning):
        log = EventLog("event_log", path=tmp_path)
        log.log_event("a", "b", "c", "d")

    # open second unrelated log
    log2 = EventLog("behavior", path=tmp_path, ring_size=10)
    assert len(log) != len(log2), "Event logs are not separate"


@pytest.mark.parametrize("element_depth_", [1, 5, 10])
@pytest.mark.parametrize("element_length_", [1, 5, 10])
@pytest.mark.parametrize("ring_size_", [1, 5, 10])
@pytest.mark.parametrize("data_type_", [np.uint8, np.uint16, np.uint32, np.uint64,
                                        np.int8, np.int16, np.int32, np.int64,
                                        np.float16, np.float32, np.float64])
def test_ring_buffer(tmp_path, helper, element_depth_, element_length_, ring_size_, data_type_):
    # instantiate
    file_path = tmp_path.joinpath("ring_buffer_test")
    rbf = RingBuffer(element_depth=element_depth_,
                     element_length=element_length_,
                     ring_size=ring_size_,
                     path=file_path,
                     dtype=data_type_)
    data = [np.full((element_depth_, element_length_), block, dtype=data_type_) for block in range(25)]

    # test utilization
    for block in data:
        rbf.add_data(block)

    # test get_data calls
    np.testing.assert_array_equal(rbf(), rbf.get_data(), "Mismatched get_data calls")

    # test closing
    rbf.close()

    # test reorganization
    org_data = np.memmap(rbf.org_path, shape=rbf.data_shape, dtype=rbf.data_type)
    np.testing.assert_equal(np.hstack(data), org_data)

    # test print
    with helper.block_printing():
        print(rbf)

    # test clear
    rbf.clear()
    assert (len(rbf) == 0), "Uncleared buffer"

    # test shape exception handling
    with pytest.warns(DataReorganizationWarning):
        rbf._validate_raw(np.ones((42,)))


@pytest.mark.parametrize("element_depth_", [1, 5, 10])
@pytest.mark.parametrize("element_length_", [1, 5, 10])
@pytest.mark.parametrize("ring_size_", [1, 5, 10])
@pytest.mark.parametrize("data_type_", [np.uint8, np.uint16, np.uint32, np.uint64,
                                        np.int8, np.int16, np.int32, np.int64,
                                        np.float16, np.float32, np.float64])
def test_timestamped_ringbuffer(tmp_path, helper, element_depth_, element_length_, ring_size_, data_type_):
    # instantiate
    file_path = tmp_path.joinpath("ring_buffer_test")
    rbf = TimestampedRingBuffer(element_depth=element_depth_,
                                element_length=element_length_,
                                ring_size=ring_size_,
                                path=file_path,
                                dtype=data_type_)
    data = [np.full((element_depth_, element_length_), block, dtype=data_type_) for block in range(25)]

    # test utilization
    for block in data:
        rbf.add_data(block)

    # test get_data calls
    np.testing.assert_array_equal(rbf(), rbf.get_data(), "Mismatched get_data calls")
    assert (len(rbf) == len(rbf.get_timestamps())), "Mismatched timestamps"

    # test closing
    rbf.close()

    # test reorganization
    org_data = np.memmap(rbf.org_path, shape=rbf.data_shape, dtype=rbf.data_type)
    np.testing.assert_equal(np.hstack(data), org_data)

    # test print
    with helper.block_printing():
        print(rbf)

    # test clear
    rbf.clear()
    assert (len(rbf) == 0), "Uncleared buffer"
    assert (len(rbf.timestamps) == 0), "Uncleared timestamps"

    # test shape exception handling
    with pytest.warns(DataReorganizationWarning):
        rbf._validate_raw(np.ones((42,)))


@pytest.mark.parametrize("ring_size_", [1, 5, 10])
def test_timestamping(tmp_path, helper, ring_size_):
    # instantiate
    file_path = tmp_path.joinpath("ring_buffer_test")
    rbf = Timestamping(path=file_path, ring_size=ring_size_)

    # test utilization
    for _ in range(25):
        rbf.add_data()

    # test get_data calls
    np.testing.assert_array_equal(rbf(), rbf.get_data(), "Mismatched get_data calls")

    # test closing
    rbf.close()

    # test print
    with helper.block_printing():
        print(rbf)

    # test clear
    rbf.clear()
    assert (len(rbf) == 0), "Uncleared buffer"

    # test shape exception handling
    with pytest.warns(DataReorganizationWarning):
        rbf._validate_raw(np.ones((42,)))
