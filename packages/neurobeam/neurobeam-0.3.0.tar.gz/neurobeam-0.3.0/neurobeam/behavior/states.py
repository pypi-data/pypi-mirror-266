from sys import float_info as _float_info
from typing import Any, Callable, Optional, Union
from random import shuffle

import numpy as np

from ..configs import CallbackRequestConfig
from ..timing import Seconds, Time, timer
from ..requests import fake_callback, CallbackRequest
from ..registries import BehaviorRegistry, Provider
from ..requests import fake_callback, CallbackRequest, TriggerRequest
from ..tools import HAS


# constants used for defaults
MIN = _float_info.min
MAX = _float_info.max


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Standard Base State
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@BehaviorRegistry.register()
@Provider()
class State:
    """
    State within the behavioral state machine.

    :param name: name of state
    :param event_log: event log for state
    :param duration: duration of state before auto-transition
    :param entry_callbacks: callbacks for entry into state
    :param exit_callbacks: callbacks for exit from state
    :param triggers: triggers for state
    """

    def __init__(self,
                 name: str,
                 event_log: Optional[Callable] = None,
                 duration: Optional["Time"] = None,
                 entry_callbacks: Optional[Union[CallbackRequestConfig, CallbackRequest, Callable]] = None,
                 exit_callbacks: Optional[Union[CallbackRequestConfig, CallbackRequest, Callable]] = None,
                 triggers: Optional = None,
                 ):
        ################################################################################################################
        # GENERAL CONFIGURATION
        ################################################################################################################
        #: str: name of state
        self.name = name
        #: "Time": duration of state before an auto-transition
        self.duration = duration
        #: Optional: triggers in the state
        self.triggers = triggers

        if HAS(triggers):
            self.triggers = [TriggerRequest(key=key, wildcard=wildcard) for key, wildcard in triggers]

        ################################################################################################################
        # CALLBACKS
        ################################################################################################################
        #: bool: whether entry/exit callbacks are currently wrapped for event logging
        self.__callbacks_wrapped = False
        if HAS(entry_callbacks) and isinstance(entry_callbacks, CallbackRequestConfig):
            entry_callbacks = CallbackRequest(requesting_instance=self,
                                              key=entry_callbacks.key,
                                              alias="__entry_callback__",
                                              approximate=entry_callbacks.approximate,
                                              required=entry_callbacks.required,
                                              arguments=entry_callbacks.arguments)
        if HAS(exit_callbacks) and isinstance(exit_callbacks, CallbackRequestConfig):
            exit_callbacks = CallbackRequest(requesting_instance=self,
                                             key=exit_callbacks.key,
                                             alias="__exit_callback__",
                                             approximate=exit_callbacks.approximate,
                                             required=exit_callbacks.required,
                                             arguments=exit_callbacks.arguments)

        self.__entry_callback__ = entry_callbacks if HAS(entry_callbacks) \
            else fake_callback("__entry_callback__")  # noqa: U100
        self.__exit_callback__ = exit_callbacks if HAS(exit_callbacks) \
            else fake_callback("__exit_callback__")  # noqa: U100

        ################################################################################################################
        # LOGGING
        ################################################################################################################
        self.__log_event__ = lambda *args: None  # noqa: U100
        self.__event_wrapper__ = lambda func: func  # noqa: U100
        if event_log:
            self.__log_event__ = event_log.log_event
            self.__event_wrapper__ = event_log.wrap

        ################################################################################################################
        # PRE-ALLOCATE
        ################################################################################################################
        #: int: number of entries into state
        self.entries = 0
        #: int: number of exits from state
        self.exits = 0
        #: float: start of state
        self.start_time = MIN
        #: float: auto-transition time
        self.auto_time = MAX
        #: float: progress of state
        self.state_progress = 0.0

        ################################################################################################################
        # SET CHECK FUNCTIONS
        ################################################################################################################
        self.check_progress = self.check_progress if HAS(self.duration) else lambda time: 0.0  # noqa: U100
        self.check_transition = self.check_transition if HAS(self.duration) else lambda time: False  # noqa: U100
        self.check_triggers = self.check_triggers if HAS(self.triggers) else lambda time: None  # noqa: U100

    @property
    def callbacks_wrapped(self) -> bool:
        return self.__callbacks_wrapped

    def wrap_callbacks(self) -> None:
        if not self.__callbacks_wrapped:
            self.__entry_callback__ = self.__event_wrapper__(self.__entry_callback__)
            self.__exit_callback__ = self.__event_wrapper__(self.__exit_callback__)
            self.__callbacks_wrapped = True

    def __str__(self):
        return f"{self.name} state with {self.entries} entries and {self.exits} exits"

    def state_loop(self, time: float) -> bool:
        self.state_progress = self.check_progress(time)
        self.check_triggers(time)
        return self.check_transition(time)

    def check_triggers(self) -> None:
        for trigger in self.triggers:
            trigger.trigger(time)

    def check_progress(self, time: float) -> float:
        return ((time - self.start_time) / self.duration) * 100

    def check_transition(self, time: float) -> bool:
        return time >= self.auto_time

    def initialize(self) -> "State":
        """
        Initialize state
        """
        self.start_time = timer()
        self.entries += 1
        self.__log_event__(self.name, "entry")

        # set duration
        if HAS(self.duration):
            self.auto_time = self.start_time + self.duration
        # TODO POTENTIAL OVERFLOW???

        if isinstance(self.triggers, list):
            for trigger in self.triggers:
                trigger.initialize(self.start_time)

        # run entry callback
        self.__entry_callback__()

    def transition(self) -> "State":
        self.exits += 1
        self.__exit_callback__()
        self.__log_event__(self.name, "exit")

    def __eq__(self, other: Any):
        return self.name == other

    def __ne__(self, other: Any):
        return self.name != other

    def __hash__(self):
        return id(self)

    def __name__(self):
        return f"State: {self.name}"


@BehaviorRegistry.register()
class Setup(State):
    #: str: key for event log (debugging)
    _event_log_key = "event_log"

    def __init__(self, event_log: Optional[Union[str, Callable]] = None, **kwargs):
        super().__init__(name="Setup", event_log=event_log)

    def initialize(self) -> "State":
        if self.entries != 0:
            raise InvalidStateEntryError(self.name)
        super().initialize()


@BehaviorRegistry.register()
class End(State):
    def __init__(self, event_log: Optional[Callable] = None, **kwargs):

        final_callback = CallbackRequest(self,
                                         "reporting_console_task_finished",
                                         alias="__entry_callback__")

        super().__init__(name="End", event_log=event_log, entry_callbacks=final_callback)

    def initialize(self) -> "State":
        if self.entries != 0:
            raise InvalidStateEntryError(self.name)
        super().initialize()


@BehaviorRegistry.register()
class Retract(State):
    def __init__(self, event_log: Optional[Callable] = None, **kwargs):
        entry_callback = CallbackRequest(self,
                                         "linear_actuator_command",
                                         alias="__entry_callback__",
                                         required=True,
                                         arguments={"value": 0.0}
                                         )
        duration = Seconds(5)
        super().__init__(name="Retract", entry_callbacks=entry_callback, duration=duration, event_log=event_log)


@BehaviorRegistry.register()
class Release(State):
    def __init__(self, event_log: Optional[Callable] = None, **kwargs):
        entry_callback = CallbackRequest(self,
                                         "linear_actuator_command",
                                         alias="__entry_callback__",
                                         required=True,
                                         arguments={"value": 100.0})
        duration = Seconds(5)
        super().__init__(name="Release", entry_callbacks=entry_callback, duration=duration, event_log=event_log)


@BehaviorRegistry.register()
@Provider()
class Selector:
    def __init__(self,
                 name: str,
                 includes: dict[str, int],
                 final: str,
                 event_log: Optional[Callable] = None,
                 **kwargs
                 ):
        ######################################################################################################
        # INITIALIZATION
        ######################################################################################################
        #: str: name of selector
        self.name = name
        self.index = []
        assert len(set(includes.values())) == 1, "All includes must have the same number of trials"
        num_blocks = list(includes.values())[0]
        unique_states = list(range(len(includes.keys())))

        for _ in range(num_blocks):
            block = unique_states.copy()
            shuffle(block)
            self.index.extend(block)

        #for idx, kv in enumerate(includes.items()):
        #    key, value = kv
        #    for _ in range(value):
        #        self.index.append(idx)
        #shuffle(self.index)
        self.index.append(len(includes.keys()))
        ######################################################################################################
        # LOGGING
        ######################################################################################################
        self.__log_event__ = lambda *args: None  # noqa: U100

        ######################################################################################################
        # PRE-ALLOCATE
        ######################################################################################################
        #: int: number of entries into state
        self.entries = 0
        #: int: number of exits from state
        self.exits = 0
        self.state_progress = 0

    def __str__(self):
        return f"{self.name}({self.index})"

    def state_loop(self, time: float) -> bool:
        return True

    def initialize(self):
        self.entries += 1
        self.__log_event__(self.name, "entry")

    def transition(self) -> "State":
        self.exits += 1
        self.__log_event__(self.name, "exit")
        try:
            return self.index[self.exits - 1]
        except IndexError:
            print(f"{self=}")
            print(f"{self.index=}")
            print(f"{self.entries=}")
            print(f"{self.exits=}")

    def __eq__(self, other: Any):
        return self.name == other

    def __ne__(self, other: Any):
        return self.name != other

    def __name__(self):
        return f"State: {self.name}"

    @property
    def callbacks_wrapped(self) -> bool:
        return True

    def wrap_callbacks(self) -> None:
        pass


@BehaviorRegistry.register()
class VariableState(State):
    def __init__(self,
                 name: str,
                 duration: "Time",
                 statistics: dict,
                 event_log: Optional[Callable] = None,
                 entry_callbacks:  Optional[Union[CallbackRequestConfig, CallbackRequest, Callable]] = None,
                 exit_callbacks:  Optional[Union[CallbackRequestConfig, CallbackRequest, Callable]] = None,
                 triggers: Optional[Union[CallbackRequestConfig, CallbackRequest, Callable]] = None,
                 **kwargs
                 ):

        if "std" not in statistics:
            warnings.warn("NO STD")

        self.duration_std = statistics.get("std")
        self.duration_mean = duration
        self.duration_lower_limit = statistics.get("lower_limit", 0)
        self.duration_upper_limit = statistics.get("upper_limit", MAX)

        super().__init__(name, event_log, duration, entry_callbacks, exit_callbacks, stimulus)

    def initialize(self) -> "VariableState":
        self.duration = np.random.normal(self.duration_mean, self.duration_std)
        self.duration = max(self.duration, self.duration_lower_limit)
        self.duration = min(self.duration, self.duration_upper_limit)
        super().initialize()
