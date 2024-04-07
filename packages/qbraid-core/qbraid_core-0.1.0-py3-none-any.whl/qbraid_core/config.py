# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for saving/loading configuration to/from the qbraidrc file.

"""

import configparser
import os
from pathlib import Path

from .exceptions import ConfigError

DEFAULT_CONFIG_SECTION = "default"
DEFAULT_ENDPOINT_URL = "https://api.qbraid.com/api"
DEFAULT_CONFIG_PATH = Path.home() / ".qbraid" / "qbraidrc"
USER_CONFIG_PATH = os.getenv("QBRAID_CONFIG_FILE", str(DEFAULT_CONFIG_PATH))


def load_config(filepath: str = USER_CONFIG_PATH) -> configparser.ConfigParser:
    """Load the configuration from the file."""
    config_path = Path(filepath)
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
    except (FileNotFoundError, PermissionError, configparser.Error) as err:
        raise ConfigError(f"Failed to load configuration from {config_path}.") from err

    return config


def save_config(config: configparser.ConfigParser, filepath: str = USER_CONFIG_PATH) -> None:
    """Save configuration to qbraidrc file."""
    try:
        config_file = Path(filepath)
        config_path = config_file.parent

        config_path.mkdir(parents=True, exist_ok=True)
        with (config_file).open("w", encoding="utf-8") as configfile:
            config.write(configfile)
    except Exception as err:
        raise ConfigError(f"Failed to save configuration to {config_file}.") from err
