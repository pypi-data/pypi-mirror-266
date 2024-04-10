# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module serving qBraid system information.

.. currentmodule:: qbraid_core.system

Classes
--------

.. autosummary::
   :toctree: ../stubs/

   FileManager

Functions
----------

.. autosummary::
   :toctree: ../stubs/

   is_exe
   is_valid_python
   get_python_version_from_cfg
   get_python_version_from_exe
   get_venv_site_packages_path
   get_active_site_packages_path
   get_local_package_path
   get_local_package_version
   get_latest_package_version
   replace_str
   echo_log

Exceptions
------------

.. autosummary::
   :toctree: ../stubs/

   QbraidSystemError
   UnknownFileSystemObjectError

"""
from .exceptions import QbraidSystemError, UnknownFileSystemObjectError
from .executables import (
    get_python_version_from_cfg,
    get_python_version_from_exe,
    is_exe,
    is_valid_python,
)
from .generic import echo_log, replace_str
from .packages import (
    get_active_site_packages_path,
    get_latest_package_version,
    get_local_package_path,
    get_local_package_version,
    get_venv_site_packages_path,
)
from .threader import FileManager
