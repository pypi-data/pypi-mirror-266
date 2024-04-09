import pytest

from neurobeam.controller import Controller
from neurobeam.exceptions import (EmptyControllerError, EmptyControllerWarning, InvalidAdapterWarning,
                                  InvalidComponentWarning, SingletonError, ControllerImmutabilityWarning)


def test_controller_empty_warning():
    with pytest.warns(EmptyControllerWarning):
        controller = Controller()

    with pytest.raises(EmptyControllerError):
        controller.start()

    with pytest.raises(EmptyControllerError):
        controller.stop()

    with pytest.raises(EmptyControllerError):
        controller.destroy()


# noinspection PyPep8Naming
def test_controller_invalid_args(MockComponent, helper):
    # test warn bad argument at init
    with pytest.warns((InvalidAdapterWarning, InvalidComponentWarning)):
        with helper.BlockPrinting():
            controller = Controller((MockComponent, helper.empty_class()))


# noinspection PyPep8Naming
def test_controller(MockComponent, helper):  # MockReadInterface, MockWriteInterface, MockTriggerInterface, helper):
    mc0 = MockComponent()
    mc1 = MockComponent()
    controller = Controller(mc0)  # MockReadInterface, MockWriteInterface, MockTriggerInterface))

    # test collected
    assert controller.components == [mc0, ]
    # assert controller.adapters == [MockReadInterface, MockWriteInterface, MockTriggerInterface]

    # test manually added
    controller.add_component(mc1)
    for component in controller.components:
        assert isinstance(component, MockComponent)

    # controller.add_adapter(MockReadInterface)
    # assert controller.adapters == [MockReadInterface, MockWriteInterface, MockTriggerInterface, MockReadInterface]

    # test start
    with helper.BlockPrinting():
        controller.start()

    # test tuple conversion
    assert isinstance(controller.components, tuple)
    assert isinstance(controller.adapters, tuple)

    # test immutability
    with pytest.warns(ControllerImmutabilityWarning):
        controller.add_component(mc0)

    # test stop
    with helper.BlockPrinting():
        controller.stop()

