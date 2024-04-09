from functools import partial
from typing import Union, Tuple, Any, Optional

from ..extensions import BehaviorState
from ..registries import BehaviorRegistry
from ..tools import HAS


@BehaviorRegistry.register()
def state_transition(origin: "BehaviorState", target: "BehaviorState") -> "BehaviorState":
    # noinspection PyNoneFunctionAssignment
    origin.transition()
    target.initialize()
    return target


@BehaviorRegistry.register()
def ordered_transition(origin: "BehaviorState",
                       targets: Tuple["BehaviorState", ...],
                       order: Tuple[int, ...],
                       final_target: Optional["BehaviorState"] = None) -> "BehaviorState":

    state_map = {idx: state for idx, state in enumerate(targets)}

    if HAS(final_target):
        final_id = len(targets)
        state_map[final_id] = final_target

    def inner_generator():
        return (partial(state_transition, origin=origin, target=state_map[idx]) for idx in order)

    def outer_generator(inner_generator_):
        return (func() for func in inner_generator_)

    def iterator(outer_generator_):
        try:
            return next(outer_generator_)
        except StopIteration:
            raise StopIteration

    return iterator(outer_generator(inner_generator()))
