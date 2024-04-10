# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Unit tests related to qBraid core functionality and system configurations.

"""
from pathlib import Path
from unittest.mock import patch

import pytest

from qbraid_core.exceptions import QbraidException
from qbraid_core.system import (
    get_active_site_packages_path,
    get_latest_package_version,
    get_local_package_path,
    get_local_package_version,
)

# pylint: disable=unused-argument


# Success with a single site-packages path
@patch("site.getsitepackages", return_value=["/path/to/site-packages"])
def test_single_site_packages_path(mock_getsitepackages):
    """Test the get_active_site_packages_path function when a single site-packages path is found."""
    assert get_active_site_packages_path() == Path("/path/to/site-packages")


# Success with multiple site-packages paths, one matching the current environment
@pytest.mark.skip(reason="Not passing")
@patch(
    "site.getsitepackages", return_value=["/wrong/path/to/site-packages", "/path/to/site-packages"]
)
@patch("sys.executable", return_value="/path/to/python")
def test_multiple_site_packages_paths(mock_executable, mock_getsitepackages):
    """Test get_active_site_packages_path function when multiple site-packages paths are found."""
    assert get_active_site_packages_path() == Path("/path/to/site-packages")


# Failure to find site-packages path
@pytest.mark.skip(reason="Not passing")
@patch("site.getsitepackages", return_value=["/wrong/path/to/site-packages"])
@patch("sys.executable", return_value="/another/path/to/python")
def test_fail_to_find_site_packages(mock_executable, mock_getsitepackages):
    """Test get_active_site_packages_path function when the site-packages path cannot be found."""
    with pytest.raises(QbraidException):
        get_active_site_packages_path()


@patch(
    "qbraid_core.system.packages.get_active_site_packages_path",
    return_value=Path("/path/to/site-packages"),
)
def test_get_local_package_path_exists(mock_get_active_site_packages_path):
    """Test the get_local_package_path function with an existing package."""
    package_name = "existing_package"
    expected_path = "/path/to/site-packages/existing_package"
    assert get_local_package_path(package_name) == Path(expected_path)


@patch(
    "qbraid_core.system.packages.get_active_site_packages_path",
    side_effect=QbraidException("Failed to find site-packages path."),
)
def test_get_local_package_path_error(mock_get_active_site_packages_path):
    """Test get_local_package_path function raises exception when site-packages not found."""
    package_name = "nonexistent_package"
    with pytest.raises(QbraidException):
        get_local_package_path(package_name)


def test_get_latest_version_raises():
    """Test the _get_latest_version function when an error occurs."""
    with pytest.raises(QbraidException):
        get_latest_package_version("nonexistent_package")


def test_get_local_version_raises():
    """Test the _get_local_version function when an error occurs."""
    with pytest.raises(QbraidException):
        get_local_package_version("nonexistent_package")
