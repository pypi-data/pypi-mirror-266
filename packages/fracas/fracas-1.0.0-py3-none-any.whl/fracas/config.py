import json
import os.path

import yaml

from . import dialog

CONFIG = {}
HOME = "~"


def get(key):
    return CONFIG.get(key)


def read():
    """Read config file if found, or run setup().

    Returns:
        config dictionary.
    """
    try:
        path = os.path.join(os.path.expanduser(HOME), ".fracas")
        with open(path, "r") as f:
            CONFIG.update(yaml.safe_load(f))
    except FileNotFoundError:
        CONFIG.update(setup())


def setup():
    """Setup config file.

    Returns:
        config dictionary.
    """
    config_path = os.path.join(os.path.expanduser(HOME), ".fracas")
    data = dialog.welcome()
    with open(config_path, "w") as f:
        yaml.dump(data, f)
    return data
