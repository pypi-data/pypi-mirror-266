from functools import partial
from sys import float_info as _float_info
from threading import Thread
from time import sleep
from typing import Callable, Union

from frozendict import frozendict
import numpy as np

from ..registries import BehaviorRegistry, Provider
from ..requests import CallbackRequest
from ..timing import timer

# Constants
MIN = _float_info.min
MAX = _float_info.max


@BehaviorRegistry.register()
@Provider()
class Machine(Thread):
    """
    Behavioral state machine
    """
    def __init__(self,
                 states: dict[str, "BehaviorState"],
                 transitions: dict[str, Callable],
                 event_log: "EventLog",
                 reporting_interval: float):
        ################################################################################################################
        # INITIALIZE
        ################################################################################################################
        #: Union[dict[str, "BehaviorState"], frozendict[str, "BehaviorState"]]: states
        self.states = states
        #: Union[dict[str, partial], frozendict[str, partial]]: transitions
        self.transitions = transitions
        #: float: reporting interval (microseconds)
        self.reporting_interval = reporting_interval
        #: bool: running flag
        self.running = False
        #: float: next time to report
        self.next_report_time = MAX
        #: float: progress of state
        self.state_progress = 0.0
        #: float: progress of task
        self.task_progress = 0.0
        #: bool: whether the behavioral state machine is locked into its build
        self._locked = False
        self._current_state = None

        ################################################################################################################
        # Request Callbacks
        ################################################################################################################
        #: start_callback: Callable: start callback
        self.startup = CallbackRequest(self, key="reporting_console_task_start", alias="startup")

        #: end_callback: Callable: end callback
        self.end_experiment = CallbackRequest(self, key="destroy", alias="end_experiment")

        #: Tuple[Callable]: reporting callbacks
        self.reporting_progress_state = CallbackRequest(self, key="reporting_console_progress_state",
                                                        alias="reporting_progress_state",
                                                        )
        self.reporting_progress_task = CallbackRequest(self, key="reporting_console_progress_task",
                                                       alias="reporting_progress_task",
                                                       )

        ################################################################################################################
        # PRE-ALLOCATE
        ################################################################################################################
        self.current_state = self.states.get("Setup")

        ################################################################################################################
        # Instantiate Thread
        ################################################################################################################
        Thread.__init__(self, name="BehavioralMachine")

    @property
    def locked(self) -> bool:
        return self._locked

    @property
    def current_state(self) -> "BehaviorState":
        return self._current_state.name

    @locked.setter
    def locked(self, value: bool) -> None:
        if value and not self._locked:
            self.states = frozendict(self.states)
            self.transitions = frozendict(self.transitions) if self.transitions else frozendict()
            self._locked = value
        elif not value and self._locked:
            raise TypeError
        # TODO: import correct error

    @current_state.setter
    def current_state(self, state: "BehaviorState") -> "_BehavioralStateMachine":
        self._current_state = state

    def wrap_all_callbacks(self) -> "_BehavioralStateMachine":
        for state in self.states.values():
            state.wrap_callbacks()

    def start(self) -> "_BehavioralStateMachine":
        self.wrap_all_callbacks()
        self.locked = True
        self._current_state.initialize()
        self.running = True
        self.startup()
        self.next_report_time = timer() + self.reporting_interval
        self.current_state = self.transitions.get("Setup")()
        Thread.start(self)  # Call Thread start method

    def stop(self) -> "_BehavioralStateMachine":
        self.running = False

    def run(self) -> "_BehavioralStateMachine":
        while self.running:
            time = timer()
            if self._current_state.state_loop(time):
                self.current_state = self.transitions.get(self.current_state)()
            self.update_progress()
            self.check_reporting(time)
            self.release_gil()
            if self.current_state == "End":
                self.running = False
                self.end_experiment()
                break

    def check_reporting(self, time: float) -> "_BehavioralStateMachine":
        if time >= self.next_report_time:
            self.reporting_progress_state(self.current_state, self.state_progress)
            self.reporting_progress_task("DARIK", self.task_progress)
            self.next_report_time += self.reporting_interval

    def release_gil(self) -> "_BehavioralStateMachine":
        # Use this to make sure the behavioral thread isn't clogging up the flow running excessive timer checks
        # Python 3.11 added a "high-resolution timer" that reports in the nanoseconds but when checking the polling
        # performance seems to be limited to 1/2 millisecond, and I'd like to avoid having to backport. If the argument
        # to time.sleep() is zero, you will pass the GIL instead which will hopefully avoid this light behavior hogging
        # the instruction list.

        # Update: I need to set sleep to non-zero or the GIL is still clogged...
        sleep(MIN)
        # pass

    def update_progress(self, *args, **kwargs) -> "_BehavioralStateMachine":
        self.state_progress = self._current_state.state_progress
        self.task_progress = self._check_task_progress(*args, **kwargs)

    def _check_task_progress(self, *args, **kwargs) -> float:
        return 0.0
