import pytest

from neurobeam.timing import timer, Microseconds, Milliseconds, Seconds, Minutes, Hours

import numpy as np


COVERAGE_OVERHEAD = 2.5  # overhead of running tests with coverage, which impacts timer performance


def test_timer():

    deltas = np.diff([timer() for time_step in range(25)])
    # Down from 1000 because for some reason we have large delays when using coverage
    assert (np.median(deltas) <= 2 * COVERAGE_OVERHEAD), f"Poor timer performance: median time resolution = " \
                                                         f"{np.median(deltas)}"
    assert (np.max(deltas) <= 15 * COVERAGE_OVERHEAD), f"Poor timer performance: worst case time resolution = " \
                                                       f"{np.max(deltas)}"


def test_conversions():

    test_time_hours = 1.25 / 3600
    test_time_minutes = 1.25 / 60
    test_time_seconds = 1.25
    test_time_milli = 1250
    test_time_micros = 1250000

    times = (test_time_micros, test_time_milli, test_time_seconds, test_time_minutes, test_time_hours)

    # Test base
    base_time = Microseconds(test_time_micros)
    attrs = ("microseconds", "milliseconds", "seconds", "minutes", "hours")
    for attr, unit_of_time in zip(attrs, times):
        assert (unit_of_time == getattr(base_time, attr))

    # test converters

    converters = (Microseconds, Milliseconds, Seconds, Minutes, Hours)
    for converter, unit_of_time in zip(converters, times):
        assert (test_time_micros == converter(unit_of_time))
