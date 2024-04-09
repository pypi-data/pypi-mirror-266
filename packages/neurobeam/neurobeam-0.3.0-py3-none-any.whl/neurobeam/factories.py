from functools import partial, singledispatchmethod
from typing import Union, Tuple, Optional, Callable, List
from .configs import Config, HoistedConfig, StateConfig, TransitionConfig
from .controller import Controller
from .data import EventLog
from .exceptions import MissingIdentifierError
from .extensions import Component, Adapter, BehaviorState
from .registries import AdapterRegistry, AudioRegistry, BehaviorRegistry, ComponentRegistry
from .tools import prune_keys, parse_empties, HAS, EMPTY


"""
Here are the classes and functions that are used to create the various components of the neurobeam. These factories are used
to create the adapters, components, and controller. Configs are created separating using the Config class. The GUI 
factory is located elsewhere (GUI FOLDER)
"""


class AdapterFactory:
    #: AdapterRegistry: The adapter registry to retrieve adapter constructors from
    _registry = AdapterRegistry()

    def __init__(self, config: "Config"):
        #: Config: The neurobeam configuration
        self.config = config

        #: dict: instance registry of hardware constructors with hoisted configs attached using partial functions
        self.registry = {}

        # Hoist sub-configurations to top-level namespace
        self.hoist()

    def create(self, adapter: Union[str, int]) -> "Adapter":
        if adapter not in self.registry:
            raise MissingIdentifierError(self, adapter)
        return self.registry.get(adapter)()

    def hoist(self) -> "AdapterFactory":
        """
        Hoist the factory methods to the instance registry
        """
        self.registry = \
            {idx: partial(self._registry.get(adapter.factory_key),
                          HoistedConfig(self.config, "adapters", idx))
             for idx, adapter in enumerate(self.config.adapters)}


class AudioFactory:
    #: dict: registry of audio stimulus constructors
    _registry = AudioRegistry()

    def __init__(self, speaker: "Speaker"):
        self._speaker = speaker
        self.registry = {method: partial(self._registry.get(method),
                                         self._speaker.sampling_rate,
                                         self._speaker.channels
                                         ) for method in self._registry}

    @classmethod
    def register(cls):  # noqa: ANN206
        """
        A decorator to register a method as a constructor for a specific audio stimulus type.

        """
        def register_method(method):  # noqa: ANN206, ANN001, ANN201
            cls._registry[method.__name__] = method
            return method
        return register_method

    def create(self, method: str, *args, **kwargs):
        """
        Create an audio stimulus using the specified method.

        Args:
            method (str): The method to use to create the stimulus.
            *args: The arguments to pass to the constructor.
            **kwargs: The keyword arguments to pass to the constructor.

        Returns:
            np.ndarray: The stimulus.

        """
        if "intensity" in kwargs:
            intensities = kwargs.pop("intensity")
            if isinstance(intensities, (tuple, list)):
                kwargs["volume"] = tuple([self._speaker.lut.get(intensity) for intensity in intensities])
            else:
                kwargs["volume"] = self._speaker.lut.get(intensities)
        stimulus = self.registry.get(method)(*args, **kwargs)

        return stimulus


class BehaviorFactory:
    """
    Factory for creating states and transitions for a behavioral state machine. We use a factory here to allow for
    flexibility in the creation of states and transitions, and to allow for the possibility of users creating their own
    states and transitions. This is a singleton class, as we only need one factory and we only ever have one behavioral
    state machine.
    """
    _registry = BehaviorRegistry()

    @staticmethod
    def format_state_recipe(states: Tuple[StateConfig, ...]) -> Tuple[dict, ...]:
        # format
        state_recipe = [dict(state) for state in states]
        # ensure there is a setup
        if not any([state.get("special") == "Setup" for state in state_recipe]):
            state_recipe.append({"special": "Setup"})
        # ensure there is an end
        if not any([state.get("special") == "End" for state in state_recipe]):
            state_recipe.append({"special": "End"})
        return tuple(state_recipe)

    @staticmethod
    def format_transition_recipe(transitions: Tuple[TransitionConfig, ...]) -> Tuple[dict, ...]:
        transition_recipe = [transition.dict() for transition in transitions]
        transition_recipe = tuple(transition_recipe)
        return transition_recipe

    @classmethod
    def construct(cls,
                  states: Tuple[StateConfig, ...],
                  transitions: [TransitionConfig, ...],
                  event_log: "EventLog",
                  reporting_interval: float) -> "_BehaviorFactory":
        # First construct states, then construct transitions
        # (attaching transitions to states through partials as necessary)
        state_recipe = cls.format_state_recipe(states)
        states = {state.name: state for state in cls.construct_states(state_recipe, event_log)}
        # Fail on single state, but we will always have a setup and end state... so it's ok
        transition_recipe = cls.format_transition_recipe(transitions)
        transitions = cls.construct_transitions(transition_recipe, states)
        # if isinstance(transitions, tuple) and len(transitions) == 2:
        #    transitions = {transitions[0]: transitions[1]}
        # Construct & initialize state machine
        machine = cls._registry.get("Machine")
        return machine(states, transitions, event_log, reporting_interval)

    # noinspection PyNestedDecorators
    @singledispatchmethod
    @classmethod
    def construct_states(cls,
                         state_recipe,  # noqa: U100
                         event_log: Optional["EventLog"] = None  # noqa: U100
                         ) -> Union["BehaviorState", List["BehaviorState"]]:  # noqa: U100
        raise TypeError

    # noinspection PyMethodParameters,PyNestedDecorators
    @construct_states.register
    @classmethod
    def _(cls,
          state_recipe: tuple,
          event_log: Optional["EventLog"] = None
          ) -> List["BehaviorState"]:
        return [cls.construct_states(recipe, event_log) for recipe in state_recipe]

    # noinspection PyMethodParameters,PyNestedDecorators
    @construct_states.register
    @classmethod
    def _(cls, state_recipe: dict, event_log: Optional["EventLog"] = None) -> "BehaviorState":
        state_type = state_recipe.get("special")
        if EMPTY(state_type):
            state_type = "State"
        if not cls._registry.has(state_type):
            raise MissingIdentifierError(cls, state_type)
        method = cls._registry.get(state_type)
        state_recipe = prune_keys(state_recipe, ("special", "factory_key", "version"))
        # TODO: necessary?
        state_recipe = parse_empties(state_recipe)
        # TODO: necessary?
        options = state_recipe.get("options", {})
        return method(event_log=event_log, **{**options, **state_recipe})

    # noinspection PyNestedDecorators
    @singledispatchmethod
    @classmethod
    def construct_transitions(cls,
                              transition_recipe: dict) -> "_BehavioralStateMachine":  # noqa: U100
        raise TypeError

    # noinspection PyNestedDecorators
    @construct_transitions.register
    @classmethod
    def _(cls, transition_recipe: tuple, states: dict[str, "BehaviorState"]) -> dict[str, Callable]:
        return dict(cls.construct_transitions(recipe, states) for recipe in transition_recipe)

    # noinspection PyNestedDecorators
    @construct_transitions.register
    @classmethod
    def _(cls, transition_recipe: dict, states: dict[str, "BehaviorState"]) -> Tuple[str, Callable]:
        name = transition_recipe.get("name")
        origin = transition_recipe.get("origin")
        target = transition_recipe.get("targets")
        name = name if name.lower() != "auto" else origin
        if isinstance(target, tuple):
            targets = tuple([states.get(t) for t in target])
            order = transition_recipe.get("order")
            return name, partial(cls._registry.get("ordered_transition"), states.get(origin), targets, order)
        else:
            targets = states.get(target)
            return name, partial(cls._registry.get("state_transition"), states.get(origin), targets)
# TODO: Clean up & debug


class ComponentFactory:
    #: dict: ComponentRegistry: The component registry to retrieve component constructors from
    _registry = ComponentRegistry()

    def __init__(self, config: "Config"):
        """
        Factory for creating components, as defined by :class:`Component <neurobeam.extensions.Component>`. Components are
        added to the registry using the :meth:`register` decorator.

        :raises DuplicateRegistrationError: Raised if the registration cannot be complete on a class because it would
        create duplicate registry keys.
        :raises MissingIdentifierError: Raised if the requested factory method is not in the registry.

        ..seealso:: :class:`Component <neurobeam.extensions.Component>`
        """
        #: Config: The neurobeam configuration
        self.config = config

        #: dict: instance registry of hardware constructors with hoisted configs attached using partial functions
        self.registry = {}

        # Hoist sub-configurations to top-level namespace
        self.hoist()

    def create(self, component: Union[str, int]) -> "Component":
        """
        Create a component using the specified constructor. Retrieves a partial function from the instance registry to
        automatically pass the config to the constructor.

        :param component: The factory_key or the index of the component to create
        :returns: The instantiated component.
        :raises MissingIdentifierError: Raised if the requested factory method is not in the registry.
        """
        if component not in self.registry:
            raise MissingIdentifierError(self, component)
        return self.registry.get(component)()

    def hoist(self) -> "ComponentFactory":
        """
        Hoist the factory methods to the instance registry
        """
        self.registry = \
            {idx: partial(self._registry.get(component.factory_key),
                          HoistedConfig(self.config, "components", idx))
             for idx, component in enumerate(self.config.components)}
