# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for making requests to the qBraid API.

"""
import configparser
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
import urllib3
from requests.adapters import HTTPAdapter

from .config import DEFAULT_CONFIG_SECTION, DEFAULT_ENDPOINT_URL, load_config, save_config
from .exceptions import AuthError, ConfigError, RequestsApiError, UserNotFoundError
from .registry import client_registry, discover_services
from .retry import STATUS_FORCELIST, PostForcelistRetry

if TYPE_CHECKING:
    import qbraid_core

logger = logging.getLogger(__name__)


class Session(requests.Session):
    """Custom session with handling of request urls and authentication.

    This is a child class of :py:class:`requests.Session`. It handles
    authentication with custom headers,and retries on specific 5xx errors.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *args,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        auth_headers: Optional[Dict[str, Any]] = None,
        retries_total: int = 2,
        retries_connect: int = 1,
        backoff_factor: float = 0.5,
        **kwargs,
    ):
        """
        Initialize custom session with default base_url and auth_headers.

        Args:
            base_url (optional, str): Base URL to prepend to all requests.
            headers (optional, dict): Dictionary of headers to include in all requests.
            auth_headers (optional, dict): Dictionary of authorization headers to include in all
                                           requests. Values will be masked in error messages.
            retries_total (int): Number of total retries for the requests. Default 2.
            retries_connect (int): Number of connect retries for the requests. Default 1.
            backoff_factor (float): Backoff factor (seconds) between retry attempts. Default 0.5.
        """
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.auth_headers = {}
        if auth_headers:
            self.auth_headers.update(auth_headers)
        if headers:
            self.headers.update(headers)
        self.headers.update(self.auth_headers)
        self._initialize_retry(retries_total, retries_connect, backoff_factor)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @property
    def base_url(self) -> Optional[str]:
        """Return the base URL."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: Optional[str]) -> None:
        """Set the base URL."""
        self._base_url = value

    def _initialize_retry(
        self, retries_total: int, retries_connect: int, backoff_factor: float
    ) -> None:
        """Set the session retry policy.

        Args:
            retries_total (int): Number of total retries for the requests.
            retries_connect (int): Number of connect retries for the requests.
            backoff_factor (float): Backoff factor between retry attempts.
        """
        retry = PostForcelistRetry(
            total=retries_total,
            connect=retries_connect,
            backoff_factor=backoff_factor,
            status_forcelist=STATUS_FORCELIST,
        )

        retry_adapter = HTTPAdapter(max_retries=retry)
        self.mount("http://", retry_adapter)
        self.mount("https://", retry_adapter)

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Response:
        """Construct, prepare, and send a ``Request``.
        Override the request method to prepend base_url to the URL and include additional headers.

        Args:
            method (str): HTTP method (e.g., 'get', 'post').
            url (str): URL for the request. Prepend base_url if url is a relative URL.
            **kwargs: Additional arguments for the request

        Returns:
            Response object.

        Raises:
            RequestsApiError: If the request failed.
        """
        # Prepend the base_url if it is provided and the url is relative
        if self.base_url and not url.startswith(("http://", "https://")):
            base_url = self.base_url.rstrip("/") + "/"
            url = url.lstrip("/")
            url = urljoin(base_url, url)

        try:
            response = super().request(method, url, *args, **kwargs)
            response.raise_for_status()
        except requests.RequestException as err:
            # Wrap requests exceptions for compatibility.
            message = str(err)
            if err.response is not None:
                try:
                    error_json = err.response.json()["error"]
                    msg = error_json["message"]
                    code = error_json["code"]
                    message += f". {msg}, Error code: {code}."
                    logger.debug(
                        "Response uber-trace-id: %s", err.response.headers["uber-trace-id"]
                    )
                except Exception:  # pylint: disable=broad-except
                    # the response did not contain the expected json.
                    message += f". {err.response.text}"

            for _, value in self.auth_headers.items():
                message = message.replace(value, "...")

            raise RequestsApiError(message) from err

        return response


class QbraidSession(Session):  # pylint: disable=too-many-instance-attributes
    """Custom session with handling of request urls and authentication.

    This is a child class of :py:class:`qbraid_core.sessions.Session`.
    It handles qbraid authentication with custom headers and has SSL
    verification disabled for compatibility with qBraid Lab.
    """

    def __init__(self, *args, api_key: Optional[str] = None, **kwargs) -> None:
        """Initialize custom session with default base_url and auth_headers.

        Args:
            api_key (optional, str): Authenticated qBraid API key.
        """
        self.api_key = api_key
        self.user_email = kwargs.pop("user_email", None)
        self.refresh_token = kwargs.pop("refresh_token", None)
        self.verify = False

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if "domain" not in kwargs["headers"]:
            kwargs["headers"]["domain"] = kwargs.pop("pool", "qbraid")

        if "auth_headers" not in kwargs:
            kwargs["auth_headers"] = {}
        if self.api_key:
            kwargs["auth_headers"]["api-key"] = self.api_key
        if self.refresh_token:
            kwargs["auth_headers"]["refresh-token"] = self.refresh_token
        if self.user_email:
            kwargs["auth_headers"]["email"] = self.user_email
        super().__init__(*args, **kwargs)

    @Session.base_url.setter
    def base_url(self, value: Optional[str]) -> None:
        """Set the qbraid api url."""
        url = value or self.get_config("url")
        value = url or DEFAULT_ENDPOINT_URL
        value = value.rstrip("/") + "/"
        super(QbraidSession, QbraidSession).base_url.fset(self, value)

    @property
    def api_key(self) -> Optional[str]:
        """Return the api key."""
        return self._api_key

    @api_key.setter
    def api_key(self, value: Optional[str]) -> None:
        """Set the api key."""
        api_key = value or self.get_config("api-key")
        self._api_key = api_key or os.getenv("QBRAID_API_KEY")

    @property
    def user_email(self) -> Optional[str]:
        """Return the session user email."""
        return self._user_email

    @user_email.setter
    def user_email(self, value: Optional[str]) -> None:
        """Set the session user email."""
        user_email = value or self.get_config("email")
        self._user_email = user_email or os.getenv("JUPYTERHUB_USER")

    @property
    def refresh_token(self) -> Optional[str]:
        """Return the session refresh token."""
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value: Optional[str]) -> None:
        """Set the session refresh token."""
        refresh_token = value or self.get_config("refresh-token")
        self._refresh_token = refresh_token or os.getenv("REFRESH")

    def get_config(self, config_name: str) -> Optional[str]:
        """Returns the config value of specified config.

        Args:
            config_name: The name of the config
        """
        try:
            config = load_config()
        except ConfigError:
            return None

        section = DEFAULT_CONFIG_SECTION
        if section in config.sections():
            if config_name in config[section]:
                return config[section][config_name]
        return None

    def get_user(self) -> Dict[str, Any]:
        """Get user metadata.

        Returns:
            Dictionary containing user metadata.

        Raises:
            UserNotFoundError: If user metadata is invalid or not found.
        """
        try:
            metadata = self.get("/identity").json()
        except RequestsApiError as err:
            raise UserNotFoundError from err

        if not metadata:
            raise UserNotFoundError("User metadata invalid or not found.")

        return metadata

    def save_config(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs
    ) -> None:
        """Create qbraidrc file. In qBraid Lab, qbraidrc is automatically present in filesystem.

        Raises:
            UserNotFoundError: If user metadata is invalid or not found.
            AuthError: If there is a credential mismatch.
            ConfigError: If there is an error saving the config.
        """
        self.api_key = api_key or self.api_key
        self.base_url = base_url or self.base_url
        self.user_email = kwargs.get("user_email", self.user_email)
        self.refresh_token = kwargs.get("refresh_token", self.refresh_token)

        res_json = self.get_user()
        res_email = res_json.get("email")

        if self.user_email and self.user_email != res_email:
            raise AuthError(
                f"Credential mismatch: Session initialized for '{self.user_email}', \
                    but API key corresponds to '{res_email}'."
            )

        try:
            config = configparser.ConfigParser()
            section = DEFAULT_CONFIG_SECTION
            if section not in config.sections():
                config.add_section(section)
            if self.user_email:
                config.set(section, "email", self.user_email)
            if self.api_key:
                config.set(section, "api-key", self.api_key)
            if self.refresh_token:
                config.set(section, "refresh-token", self.refresh_token)
            if self.base_url:
                config.set(section, "url", self.base_url)
        except Exception as err:
            raise ConfigError from err

        save_config(config)

    def get_available_services(self) -> List[str]:
        """
        Get a list of available services that can be loaded as low-level
        clients via :py:meth:`Session.client`.

        Returns:
            List: List of service names.
        """
        services_path = os.path.join(os.path.dirname(__file__), "services")
        return list(discover_services(services_path))

    def client(self, service_name: str) -> "qbraid_core.QbraidClient":
        """Return a client for the specified service.

        Args:
            service_name: Name of the service.

        Returns:
            qbraid_core.QbraidClient: Client for the specified service.
        """
        if len(client_registry) == 0:
            self.get_available_services()
        client_class = client_registry.get(service_name)
        if not client_class:
            raise ValueError(f"Service '{service_name}' not registered")
        return client_class(session=self)
