# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for checking state of qBraid Quantum Jobs proxies.

"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from qbraid_core.system import get_active_site_packages_path, get_venv_site_packages_path

from .exceptions import QbraidException

logger = logging.getLogger(__name__)

SUPPORTED_QJOB_LIBS = ["braket"]


def _check_proxy(
    proxy_spec: Tuple[str, ...], slug_path: Optional[Path] = None
) -> Tuple[bool, bool, Path]:
    """
    Checks if the specified proxy file exists and contains the string 'qbraid'.

    Args:
        proxy_spec (Tuple[str, ...]): A tuple specifying the path components from 'site-packages'
                                      to the target proxy file, e.g. ("botocore", "httpsession.py").
        slug_path (optional, Path): The base path to prepend to the 'pyenv' directory.

    Returns:
        A tuple of two booleans and sitepackages path: The first bool indicates whether the
        specified proxy file exists; the second bool, if the file exists, is True if it contains
        'qbraid', False otherwise. The sitepackages path gives the location of the site-packages
        directory where the proxy file is located.
    """
    site_packages_path = None

    try:
        if slug_path is None:
            site_packages: str = get_active_site_packages_path()
            site_packages_path = Path(site_packages)
        else:
            site_packages_path = get_venv_site_packages_path(slug_path / "pyenv")
    except QbraidException as err:
        logger.debug(err)
        return False, False, site_packages_path

    target_file_path = site_packages_path.joinpath(*proxy_spec)

    if not target_file_path.exists():
        return False, False, site_packages_path

    try:
        with target_file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if "qbraid" in line:
                    return True, True, site_packages_path
        return True, False, site_packages_path
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.debug("Unexpected error checking qBraid proxy: %s", err)

    return True, False, site_packages_path


def quantum_lib_proxy_state(device_lib: str, **kwargs) -> Dict[str, Union[str, bool]]:
    """Checks if qBraid Quantum Jobs are supported and if so, checks whether they are enabled.
    Returns dictionary providing information about the state of qBraid Quantum Jobs support
    and configuration for the given quantum device library.

    Args:
        device_lib (str): The name of the quantum device library, e.g., "braket".

    Returns:
        dict: A dictionary containing the following keys:
            - 'proxy_lib' (str): The name of the python library that would be modified by the
                                 quantum jobs proxy.
            - 'supported' (bool): Indicates whether the necessary proxy file exists for the
                                  specified quantum device library.
            - 'enabled' (bool): True if the library is configured to support qBraid Quantum Jobs,
                                False otherwise.
    """
    state = {
        "proxy_lib": None,
        "supported": False,
        "enabled": False,
    }

    if device_lib not in SUPPORTED_QJOB_LIBS:
        raise ValueError(f"Unsupported quantum job library. Expected one of {SUPPORTED_QJOB_LIBS}")

    if device_lib == "braket":
        proxy_lib = "botocore"
        proxy_spec = (proxy_lib, "httpsession.py")
        supported, enabled, path = _check_proxy(proxy_spec, **kwargs)

    # add more device libraries here as needed

    state["proxy_lib"] = proxy_lib
    state["supported"] = supported
    state["enabled"] = enabled
    state["path"] = str(path)
    return state
