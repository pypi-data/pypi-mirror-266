# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for serving information about Python packages.

"""
import logging
import site
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import requests

from .exceptions import QbraidSystemError
from .executables import get_python_version_from_cfg, get_python_version_from_exe

logger = logging.getLogger(__name__)


def get_venv_site_packages_path(venv_path: Path) -> Path:
    """
    Determines the site-packages directory for a given virtual environment in an OS-agnostic manner.
    Automatically selects the Python version if a single version is present in the 'lib' directory.
    If multiple versions are detected, it attempts to determine the correct version through
    configuration files or the Python executable.

    Args:
        venv_path (pathlib.Path): The path to the virtual environment directory.

    Returns:
        A Path object pointing to the site-packages directory, or None if unable to determine.

    Raises:
        QbraidSystemError: If an error occurs while determining the site-packages path.
    """
    if sys.platform == "win32":
        return venv_path / "Lib" / "site-packages"

    python_dirs = sorted(venv_path.glob("lib/python*"))
    if not python_dirs:
        raise QbraidSystemError("No Python directories found in the virtual environment.")

    if len(python_dirs) == 1:
        return python_dirs[0] / "site-packages"

    python_version = get_python_version_from_cfg(venv_path)
    python_version = python_version or get_python_version_from_exe(venv_path)

    if not python_version:
        raise QbraidSystemError("Unable to determine Python version from the virtual environment.")

    major_minor_version = ".".join(python_version.split(".")[:2])
    lib_python_dir = venv_path / f"lib/python{major_minor_version}"
    return lib_python_dir / "site-packages"


def get_active_site_packages_path() -> Path:
    """Retrieves the site-packages path of the current Python environment."""

    # List of all site-packages directories as Path objects
    site_packages_paths = [Path(path) for path in site.getsitepackages()]

    if len(site_packages_paths) == 1:
        return site_packages_paths[0]

    # Path to the currently running Python interpreter
    python_executable_path = Path(sys.executable)

    # Base path of the Python environment
    env_base_path = python_executable_path.parent.parent

    # Find the site-packages path that is within the same environment
    for path in site_packages_paths:
        if env_base_path in path.parents:
            return path

    raise QbraidSystemError("Failed to find site-packages path.")


def get_local_package_path(package: str) -> Path:
    """Retrieves the local path of a package."""
    try:
        site_packages_path = get_active_site_packages_path()
        return site_packages_path / package
    except (PackageNotFoundError, ModuleNotFoundError) as err:
        raise QbraidSystemError(f"{package} is not installed in the current environment.") from err


def get_local_package_version(package: str) -> str:
    """Retrieves the local version of a package."""
    try:
        return version(package)
    except PackageNotFoundError as err:
        raise QbraidSystemError(f"{package} is not installed in the current environment.") from err


def get_latest_package_version(package: str) -> str:
    """Retrieves the latest version of package from PyPI."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.RequestException as err:
        raise QbraidSystemError(f"Failed to retrieve latest {package} version from PyPI.") from err
