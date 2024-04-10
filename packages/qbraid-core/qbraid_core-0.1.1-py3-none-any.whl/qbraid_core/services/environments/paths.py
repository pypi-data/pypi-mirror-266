# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for serving environment information.

"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

from qbraid_core.system import is_valid_python

from .validate import is_valid_slug

logger = logging.getLogger(__name__)


def get_default_envs_paths() -> List[Path]:
    """
    Returns a list of paths to qBraid environments.

    If the QBRAID_ENVS_PATH environment variable is set, it splits the variable by ':' to
    accommodate multiple paths. If QBRAID_ENVS_PATH is not set, returns a list containing
    the default qBraid environments path (~/.qbraid/environments).

    Returns:
        A list of pathlib.Path objects representing the qBraid environments paths.
    """
    qbraid_envs_path = os.getenv("QBRAID_ENVS_PATH", str(Path.home() / ".qbraid" / "environments"))
    return [Path(path) for path in qbraid_envs_path.split(":")]


def get_env_path(slug: str) -> Path:
    """Return path to qbraid environment.

    Args:
        slug (str): The environment directory to search for.

    Returns:
        pathlib.Path: The path to the environment directory.

    Raises:
        FileNotFoundError: If the environment directory does not exist.
    """
    qbraid_env_paths = get_default_envs_paths()
    for path in qbraid_env_paths:
        if path.is_dir() and path.name == slug:
            return path / slug

    raise FileNotFoundError(f"Environment '{slug}' not found in any qBraid environment path.")


def get_tmp_dir_names(envs_path: Union[str, Path]) -> List[str]:
    """Return list of tmp directories paths in envs_path"""
    pattern = re.compile(r"^tmp\d{1,2}$")  # Regex for tmp directories

    envs_dir = Path(envs_path)

    return [d.name for d in envs_dir.iterdir() if d.is_dir() and pattern.match(d.name)]


def get_next_tmpn(tmpd_names: List[str]) -> str:
    """Return next tmp directory name"""
    tmpd_names_sorted = sorted(tmpd_names, key=lambda x: int(x[3:]))
    next_tmp_int = int(tmpd_names_sorted[-1][3:]) + 1 if tmpd_names_sorted else 0
    return f"tmp{next_tmp_int}"


def which_python(slug: str) -> str:
    """Return environment's python path"""
    try:
        slug_path = Path(get_env_path(slug))
        kernels_dir = slug_path.joinpath("kernels")
        for resource_dir in kernels_dir.iterdir():
            if "python" in resource_dir.name:
                kernel_json = resource_dir.joinpath("kernel.json")
                if kernel_json.exists():
                    with kernel_json.open(encoding="utf-8") as file:
                        data = json.load(file)
                        if data["language"] == "python":
                            python_path = data["argv"][0]
                            if is_valid_python(python_path):
                                return python_path

        # fallback: check pyenv bin for python executable
        if sys.platform == "win32":
            python_path = slug_path.joinpath("pyenv", "Scripts", "python.exe")
        else:
            python_path = slug_path.joinpath("pyenv", "bin", "python")
        if is_valid_python(python_path):
            return str(python_path)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error determining Python path: %s", err)

    return sys.executable


def installed_envs_data() -> Tuple[Dict[str, Path], Dict[str, str]]:
    """Gather paths and aliases for all installed qBraid environments."""
    installed = {}
    aliases = {}

    qbraid_env_paths: List[Path] = get_default_envs_paths()

    for env_path in qbraid_env_paths:
        for entry in env_path.iterdir():
            if entry.is_dir() and is_valid_slug(entry.name):
                installed[entry.name] = entry

                if entry.name == "qbraid_000000":
                    aliases["default"] = entry.name
                    continue

                state_json_path = entry / "state.json"
                if state_json_path.exists():
                    try:
                        with open(state_json_path, "r", encoding="utf-8") as file:
                            data = json.load(file)
                        aliases[data.get("name", entry.name[:-7])] = entry.name
                    # pylint: disable-next=broad-exception-caught
                    except (json.JSONDecodeError, Exception):
                        aliases[entry.name[:-7]] = entry.name
                else:
                    aliases[entry.name[:-7]] = entry.name

    return installed, aliases
