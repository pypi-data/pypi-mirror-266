# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module providing client for interacting with qBraid quantum services.

"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from qbraid_core.client import QbraidClient
from qbraid_core.exceptions import RequestsApiError
from qbraid_core.registry import register_client

from .exceptions import EnvironmentServiceRequestError
from .paths import get_default_envs_paths
from .validate import is_valid_env_name, is_valid_slug


@register_client()
class EnvironmentManagerClient(QbraidClient):
    """Client for interacting with qBraid environment services."""

    # envs_paths = Optional[Union[Path, str]] = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.envs_paths = get_default_envs_paths()

    @property
    def envs_paths(self) -> List[Path]:
        """Returns a dictionary of environment paths.

        Returns:
            A dictionary containing the environment paths.
        """
        return self._envs_paths

    @envs_paths.setter
    def envs_paths(self, value: List[Path]):
        """Sets the qBraid environments paths."""
        self._envs_paths = value

    def create_environment(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new environment with the given name and description.

        Args:
            name: The name of the environment to create.
            description: Optional description of the environment.

        Returns:
            A dictionary containing the environment data.

        Raises:
            ValueError: If the environment name is invalid or the description is too long.
            EnvironmentServiceRequestError: If the create environment request fails.
        """
        if not is_valid_env_name(name):
            raise ValueError(f"Invalid environment name: {name}")

        if description and len(description) > 300:
            raise ValueError("Description is too long. Maximum length is 300 characters.")

        req_body = {
            "name": name,
            "description": description or "",
            "tags": "",  # comma separated list of tags
            "code": "",  # newline separated list of packages
            "visibility": "private",
            "kernelName": "",
            "prompt": "",
            "origin": "CLI",  # TODO: change to "CORE"
        }

        try:
            env_data = self.session.post("/environments/create", json=req_body).json()
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError("Create environment request failed") from err

        if env_data is None or len(env_data) == 0 or env_data.get("slug") is None:
            raise EnvironmentServiceRequestError(
                "Create environment request responsed with invalid environment data"
            )

        return env_data

    def delete_environment(self, slug: str) -> None:
        """Deletes the environment with the given slug.

        Args:
            slug: The slug of the environment to delete.

        Returns:
            None

        Raises:
            ValueError: If the environment slug is invalid.
            EnvironmentServiceRequestError: If the delete environment request fails.
        """
        if not is_valid_slug(slug):
            raise ValueError(f"Invalid environment slug: {slug}")

        try:
            self.session.delete(f"/environments/{slug}")
        except RequestsApiError as err:
            raise EnvironmentServiceRequestError("Delete environment request failed") from err
