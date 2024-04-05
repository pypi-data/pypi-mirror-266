# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
This top level module contains the main qBraid public functionality.

.. currentmodule:: qbraid_core

Classes
----------

.. autosummary::
   :toctree: ../stubs/

   QbraidClient
   QbraidSession
   PostForcelistRetry


Functions
----------

.. autosummary::
   :toctree: ../stubs/

   client
   setup_default_session

Exceptions
------------

.. autosummary::
   :toctree: ../stubs/

   QbraidException
   AuthError
   ConfigError
   RequestsApiError
   ResourceNotFoundError
   UserNotFoundError

"""
from .client import QbraidClient
from .exceptions import (
    AuthError,
    ConfigError,
    QbraidException,
    RequestsApiError,
    ResourceNotFoundError,
    UserNotFoundError,
)
from .retry import PostForcelistRetry
from .session import QbraidSession

try:
    # Injected in _version.py during the build process.
    from ._version import __version__
except ImportError:
    __version__ = ""

# Hold the default session in a global variable, but don't initialize it yet.
_DEFAULT_SESSION = None


def setup_default_session(**kwargs):
    """
    Set up a default session, passing through any parameters to the session
    constructor. There is no need to call this unless you wish to pass custom
    parameters, because a default session will be created for you.
    """
    global _DEFAULT_SESSION  # pylint: disable=global-statement
    _DEFAULT_SESSION = QbraidSession(**kwargs)


def _get_default_session():
    """
    Get or create a default session. If the session does not exist, it is created
    with the provided keyword arguments. If it already exists, the existing session
    is returned, ignoring any provided arguments.

    This function ensures that a session is created only once and reused, offering
    a balance between laziness and reusability.

    Args:
        **kwargs: Keyword arguments to pass to the Session constructor if creating
                  a new session.

    Returns:
        The default session instance.
    """
    if _DEFAULT_SESSION is None:
        setup_default_session()

    return _DEFAULT_SESSION


def client(*args, **kwargs):
    """
    Create a client for a specified service using the default session. If specific
    session parameters are needed, a new default session can be initialized before
    calling this function.

    Args:
        service_name (str): The name of the service for which to create the client.
        **kwargs: Keyword arguments for session customization, used only if creating
                  a new default session.

    Returns:
        A service client instance.
    """
    session = _get_default_session()
    _ = session.get_available_services()  # Ensure the session is initialized
    return session.client(*args, **kwargs)


__all__ = [
    "QbraidClient",
    "QbraidSession",
    "PostForcelistRetry",
    "client",
    "setup_default_session",
    "QbraidException",
    "AuthError",
    "ConfigError",
    "RequestsApiError",
    "ResourceNotFoundError",
    "UserNotFoundError",
]
