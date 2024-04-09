import warnings
from typing import Any, Tuple, Union, Optional, Callable, Mapping, List
from functools import partial, singledispatchmethod
from frozendict import frozendict
import numpy as np
from pathlib import Path

from ..configs import HoistedConfig, StateConfig, TransitionConfig
from ..extensions import BehaviorState
from ..data import EventLog
from ..exceptions import (InvalidStateEntryError, DuplicateRegistrationError, MissingIdentifierError)
from ..factories import BehaviorFactory
from ..registries import ComponentRegistry, Provider
from ..requests import CallbackRequest, wrap_callback_collection, fake_callback
from ..timing import Seconds, timer, Time
from ..tools import HAS, FORMAT_TERMINAL, prune_keys, parse_empties


from sys import float_info as _float_info


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// BEHAVIOR
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


@ComponentRegistry.register()
@Provider()
class Behavior:
    """
    Behavioral component.
    """
    #: str: key for event log (debugging)
    _event_log_key = "event_log"

    def __init__(self,
                 config: Optional["HoistedConfig"] = None,
                 name: str = "Behavioral Task",
                 states: Tuple["BehaviorState", ...] = (StateConfig(), ),
                 transitions: Tuple["TransitionConfig", ...] = (TransitionConfig(), ),
                 reporting_interval: float = 1.0,
                 output_folder: Path = Path.cwd()):
        ################################################################################################################
        # CONFIGURE
        ################################################################################################################
        #: "Config": configuration
        self.config = config
        output_folder = self.config.save_location if HAS(config) else output_folder
        #: "EventLog": Logs events of the behavior
        self.event_log = EventLog(key=self._event_log_key, path=output_folder, ring_size=5)
        # TODO: Remove hardcode for ring size of event log
        #: str: name of behavior
        self.name = self.config.name if HAS(config) else name
        #: Tuple["BehaviorState"]: states
        self.states = self.config.states if HAS(config) else states
        #: Tuple["TransitionConfig"]: transitions
        self.transitions = self.config.transitions if HAS(config) else transitions
        #: float: reporting interval
        self.reporting_interval = self.config.reporting_interval if HAS(config) else reporting_interval

        ################################################################################################################
        # PRE-ALLOCATE
        ################################################################################################################
        #: "_BehavioralStateMachine": state machine implementing behavior
        self.machine = None

        ################################################################################################################
        # BUILD
        ################################################################################################################
        self.build()

    def __str__(self):
        return self.name
        # TODO: Implement more informative __str__ for behavior

    def build(self) -> "Behavior":
        self.machine = BehaviorFactory.construct(states=self.states,
                                                 transitions=self.transitions,
                                                 event_log=self.event_log,
                                                 reporting_interval=self.reporting_interval)
        self.event_log.log_event("Behavior", "built")

    def start(self) -> "Behavior":
        if not self.machine.running:
            self.event_log.log_event("Behavior", "start")
            self.machine.start()

    def stop(self) -> "Behavior":
        if self.machine.running:
            self.machine.stop()
            self.event_log.log_event("Behavior", "stop")
        # self.event_log.close()

    def destroy(self) -> None:
        self.event_log.close()

    def __name__(self):
        return self.name
