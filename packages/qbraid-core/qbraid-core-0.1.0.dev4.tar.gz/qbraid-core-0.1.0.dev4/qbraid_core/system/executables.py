# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for serving information about system executables.

"""
import logging
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def is_exe(fpath: Union[str, Path]) -> bool:
    """
    Return true if fpath is a file we have access to that is executable.

    Args:
        fpath (Union[str, Path]): The file path to check.

    Returns:
        bool: True if the file exists, is not a directory, and is executable; False otherwise.
    """
    try:
        path = Path(fpath)
        if path.exists() and path.is_file():
            accessmode = os.F_OK | os.X_OK
            return (
                path.is_file()
                and os.access(path, accessmode)
                and not path.is_dir()
                and any(path.stat().st_mode & x for x in (stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH))
            )
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error checking if file is executable: %s", err)
    return False


def is_valid_python(python_path: Union[str, Path]) -> bool:
    """Return true if python_path is a valid Python executable."""
    python_path_str = str(
        python_path
    )  # Ensure python_path is a string for shutil.which and subprocess

    if shutil.which(python_path_str) is None:
        return False

    if sys.platform != "win32" and not is_exe(python_path_str):
        return False

    try:
        output = subprocess.check_output([python_path_str, "--version"], stderr=subprocess.STDOUT)
        return "Python" in output.decode()
    except subprocess.CalledProcessError:
        return False


def get_python_version_from_exe(venv_path: Path) -> Optional[str]:
    """
    Gets the Python version used in the specified virtual environment by executing
    the Python binary within the venv's bin (or Scripts) directory.

    Args:
        venv_path (Path): The path to the virtual environment directory.

    Returns:
        A string representing the Python version (e.g., '3.11.7'), or None if an error occurs.
    """
    # Adjust the path to the Python executable depending on the operating system
    python_executable = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "python"

    try:
        # Run the Python executable with '--version' and capture the output
        result = subprocess.run(
            [str(python_executable), "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Python version info could be in stdout or stderr
        version_output = result.stdout or result.stderr

        # Python 3.11.7 --> 3.11.7
        return version_output.split()[1]

    except subprocess.CalledProcessError as err:
        logger.warning("An error occurred while trying to get the Python version: %s", err)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.warning("Unexpected error: %s", err)

    return None


def get_python_version_from_cfg(venv_path: Path) -> Optional[str]:
    """
    Reads a pyvenv.cfg file within a given virtual environment directory and extracts
    the major and minor Python version.

    Args:
        venv_path (pathlib.Path): The path to the virtual environment directory.

    Returns:
        A string representing the Python version (e.g., '3.11.7'), or None if
        the version cannot be determined or the pyvenv.cfg file does not exist.
    """
    pyvenv_cfg_path = venv_path / "pyvenv.cfg"
    if not pyvenv_cfg_path.exists():
        logger.warning("pyvenv.cfg file not found in the virtual environment: %s", venv_path)
        return None

    try:
        with pyvenv_cfg_path.open("r") as file:
            for line in file:
                if line.startswith("version ="):
                    version_full = line.strip().split("=")[1].strip()
                    version_parts = version_full.split(".")
                    return f"{version_parts[0]}.{version_parts[1]}"
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.warning("An error occurred while reading %s: %s", pyvenv_cfg_path, err)

    return None
