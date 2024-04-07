# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module providing utilities for interfacing with qBraid environments

.. currentmodule:: qbraid_core.services.environments

Classes
----------

.. autosummary::
   :toctree: ../stubs/

   EnvironmentManagerClient

Functions
----------

.. autosummary::
   :toctree: ../stubs/

   create_local_venv
   install_status_codes
   update_install_status
   get_default_envs_paths
   get_env_path
   get_tmp_dir_names
   get_next_tmpn
   which_python
   is_valid_env_name
   is_valid_slug

Exceptions
------------

.. autosummary::
   :toctree: ../stubs/

   EnvironmentServiceRequestError
   EnvironmentServiceRuntimeError

"""
from .client import EnvironmentManagerClient
from .create import create_local_venv
from .exceptions import EnvironmentServiceRequestError, EnvironmentServiceRuntimeError
from .paths import (
    get_default_envs_paths,
    get_env_path,
    get_next_tmpn,
    get_tmp_dir_names,
    which_python,
)
from .state import install_status_codes, update_install_status
from .validate import is_valid_env_name, is_valid_slug
