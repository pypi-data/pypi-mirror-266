import pytest

from neurobeam.factories import ComponentFactory
from neurobeam.configs import DAQConfig, SpeakerConfig


def test_component_factory(config):
    config.save_location.mkdir(parents=True, exist_ok=True)
    config.add_component(SpeakerConfig())
    config.add_component(DAQConfig())
    factory = ComponentFactory(config)
    components = [factory.registry[component]() for component in factory.registry]
    assert len(components) == len(factory.registry)
