import pytest
from neurobeam.configs import save_config, load_config


def test_config_io(full_config, helper):
    full_config.save_location.mkdir(parents=True, exist_ok=True)
    path = full_config.generate_filename("test_config", ".toml")
    save_config(path, full_config)
    loaded = load_config(path)
    assert full_config == loaded
    with helper.BlockPrinting():
        print(loaded)
