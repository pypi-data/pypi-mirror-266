# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Unit tests for QbraidClient.

"""

import os

import pytest

from qbraid_core.client import QbraidClient
from qbraid_core.session import QbraidSession

skip_remote_tests: bool = os.getenv("QBRAID_RUN_REMOTE_TESTS", "False").lower() != "true"
REASON = "QBRAID_RUN_REMOTE_TESTS not set (requires configuration of qBraid storage)"


@pytest.mark.parametrize(
    "test_case",
    [
        ("507f1f77bcf86cd799439011", True),
        ("not-a-mongo-id", False),
        ("", False),
        ("507f1f77bcf86cd79943901Z", False),
    ],
)
def test_is_valid_object_id(test_case):
    """Test that the is_valid_mongo_id function works as expected."""
    mongo_id, is_valid = test_case
    assert QbraidClient._is_valid_object_id(mongo_id) == is_valid


def test_convert_email_symbols():
    """Test function that converts email to username."""
    email_input = "test-format.company_org@qbraid.com"
    expected_output = "test-2dformat-2ecompany-5forg-40qbraid-2ecom"
    # pylint: disable-next=protected-access
    assert QbraidClient._convert_email_symbols(email_input) == expected_output


@pytest.mark.skipif(skip_remote_tests, reason=REASON)
def test_running_in_lab():
    """Test function that checks whether qBraid Lab is running."""
    session = QbraidSession(api_key=os.getenv("QBRAID_API_KEY"))
    session = QbraidClient(session=session)
    assert not session._running_in_lab()  # pylint: disable=protected-access
