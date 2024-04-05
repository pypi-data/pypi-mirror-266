# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module defining abstract base clas for qBraid micro-service clients.

"""
import datetime
import os
import re
from typing import Optional

from ._compat import check_version
from .exceptions import AuthError, RequestsApiError, ResourceNotFoundError, UserNotFoundError
from .session import QbraidSession


class QbraidClient:
    """Base class for qBraid micro-service clients."""

    def __init__(self, session: Optional[QbraidSession] = None):
        self.session = session or QbraidSession()
        check_version("qbraid-core")

    @property
    def session(self) -> QbraidSession:
        """The QbraidSession used to make requests."""
        return self._session

    @session.setter
    def session(self, value: Optional[QbraidSession]) -> None:
        """Set the QbraidSession.

        Raises:
            AuthError: If the provided session is not valid.
        """
        qbraid_session = value or QbraidSession()
        try:
            _ = qbraid_session.get_user()
        except UserNotFoundError as err:
            raise AuthError("Access denied due to missing or invalid credentials") from err
        self._session = qbraid_session

    @staticmethod
    def _is_valid_object_id(candidate_id: str) -> bool:
        """
        Check if the provided string is a valid MongoDB ObjectId format.

        Args:
            candidate_id (str): The string to check.

        Returns:
            bool: True if the string is a valid ObjectId format, False otherwise.
        """
        try:
            return bool(re.match(r"^[0-9a-fA-F]{24}$", candidate_id))
        except (TypeError, SyntaxError):
            return False

    @staticmethod
    def _convert_email_symbols(email: str) -> Optional[str]:
        """Convert email to compatible string format"""
        return (
            email.replace("-", "-2d")
            .replace(".", "-2e")
            .replace("@", "-40")
            .replace("_", "-5f")
            .replace("+", "-2b")
        )

    def _running_in_lab(self) -> bool:
        """Check if running in the qBraid Lab environment."""
        # API interaction to confirm environment
        try:
            utc_datetime = datetime.datetime.now(datetime.UTC)
        except AttributeError:  # deprecated but use as fallback if datetime.UTC is not available
            utc_datetime = datetime.datetime.utcnow()

        try:
            formatted_time = utc_datetime.strftime("%Y%m%d%H%M%S")
            directory = os.path.join(os.path.expanduser("~"), ".qbraid", "certs")
            filepath = os.path.join(directory, formatted_time)
            os.makedirs(directory, exist_ok=True)

            # Create an empty file
            with open(filepath, "w", encoding="utf-8"):
                pass  # The file is created and closed immediately

            response = self.session.get(f"/lab/is-mounted/{formatted_time}")
            is_mounted = bool(response.json().get("isMounted", False))
        except (RequestsApiError, KeyError):
            is_mounted = False

        try:
            os.remove(filepath)
        except (FileNotFoundError, IOError):
            pass
        return is_mounted

    def user_credits_value(self) -> float:
        """
        Get the current user's qBraid credits value.

        Returns:
            float: The current user's qBraid credits value.
        """
        try:
            res = self.session.get("/billing/credits/get-user-credits").json()
            credits_value = res["qbraidCredits"]
            return float(credits_value)
        except (RequestsApiError, KeyError, ValueError) as err:
            raise ResourceNotFoundError("Credits value not found") from err
