# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module defining custom exceptions for the qBraid system module.

"""

from qbraid_core.exceptions import QbraidException


class QbraidSystemError(QbraidException):
    """Base class for errors raised by the qBraid system module."""


class UnknownFileSystemObjectError(QbraidSystemError):
    """Raised when the path does not point to a known file system object."""
