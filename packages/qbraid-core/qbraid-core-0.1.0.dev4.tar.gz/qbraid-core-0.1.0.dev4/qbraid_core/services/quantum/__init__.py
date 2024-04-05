# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module providing client for interacting with qBraid quantum services.

.. currentmodule:: qbraid_core.services.quantum

Classes
--------

.. autosummary::
   :toctree: ../stubs/

   QuantumClient


Functions
----------

.. autosummary::
   :toctree: ../stubs/

   process_device_data
   process_job_data
   quantum_lib_proxy_state

Exceptions
------------

.. autosummary::
   :toctree: ../stubs/

   QuantumServiceRequestError
   QuantumServiceRuntimeError

"""
from .adapter import process_device_data, process_job_data
from .client import QuantumClient
from .exceptions import QuantumServiceRequestError, QuantumServiceRuntimeError
from .proxy import quantum_lib_proxy_state
