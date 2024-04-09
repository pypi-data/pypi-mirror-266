import pytest
import importlib
from inspect import isclass


def test_exceptions(helper):
    probe_exceptions = importlib.import_module("neurobeam.exceptions")
    for exception_ in vars(probe_exceptions).values():
        if isclass(exception_) and issubclass(exception_, Exception):
            with pytest.raises(exception_):
                # noinspection PyArgumentList
                raise exception_(**helper.mock_arguments(exception_))
