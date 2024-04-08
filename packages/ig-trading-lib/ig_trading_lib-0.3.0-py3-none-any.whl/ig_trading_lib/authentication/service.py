import logging
from datetime import datetime
from typing import Optional

import requests
from pydantic import ValidationError

from .cache import AuthenticationCacheABC
from .models import AuthenticationResponse


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Exception raised for errors in the authentication process."""


class AuthenticationService:
    """Handles authentication with the IG Rest API."""

    def __init__(
        self,
        api_key: str,
        account_identifier: str,
        account_password: str,
        base_url: str,
        cache: Optional[AuthenticationCacheABC] = None,
    ):
        """Initialize the authentication service.
        :param api_key: Your IG API key.
        :param account_identifier: Your IG account identifier.
        :param account_password: Your IG account password.
        :param base_url: The base URL for the IG API (live or demo).
        :param cache: An optional cache to store the authentication response. Defaults to no caching
        """
        self.api_key = api_key
        self.account_identifier = account_identifier
        self.account_password = account_password
        self.base_url = base_url
        self.cache = cache
        logger.info(
            "Initialized authentication service. Caching %s.",
            "enabled" if self.cache else "disabled",
        )

    @property
    def url(self) -> str:
        """IG API endpoint for authentication."""
        return f"{self.base_url}/gateway/deal/session"

    @property
    def data(self) -> dict:
        """Your IG account credentials in a dictionary."""
        return {
            "identifier": self.account_identifier,
            "password": self.account_password,
        }

    @property
    def headers(self) -> dict:
        """Setting up the request headers."""
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json; charset=utf-8",
            "X-IG-API-KEY": self.api_key,
            "Version": "2",
        }

    def __load_from_cache(self) -> Optional[AuthenticationResponse]:
        """Load the authentication response from the cache if it exists and is not expired."""
        if self.cache:
            cached_response = self.cache.load_authentication_response()
            if cached_response and cached_response.expiry > datetime.now().timestamp():
                return cached_response
        return None

    def __save_to_cache(self, response: AuthenticationResponse) -> None:
        """Save the authentication response to the cache if it exists."""
        if self.cache:
            self.cache.save_authentication_response(response)

    def __authenticate(self) -> AuthenticationResponse:
        """Perform the POST request to authenticate with the IG REST API."""
        try:
            response = requests.post(self.url, json=self.data, headers=self.headers)
        except requests.RequestException as e:
            raise AuthenticationError(f"Authentication request failed: %s" % e)

        if response.status_code == 200:
            try:
                expiry = int(response.headers.get("expires", 0)) or int(
                    datetime.now().timestamp() + 6 * 3600
                )
                auth_response = AuthenticationResponse(  # raises ValidationError
                    cst_token=response.headers.get("CST"),
                    x_security_token=response.headers.get("X-SECURITY-TOKEN"),
                    expiry=expiry,
                    account_info=response.json(),  # raises ValueError
                )
                return auth_response
            except ValidationError as e:
                raise AuthenticationError("Invalid authentication response: %s" % e)
            except ValueError as e:
                raise AuthenticationError(
                    "Invalid account info in authentication response: %s" % e
                )
        else:
            raise AuthenticationError(
                "Authentication failed with status code %s: %s"
                % (response.status_code, response.text)
            )

    def __authenticate_and_cache(self) -> AuthenticationResponse:
        """Authenticate with the IG REST API and save the response to the cache."""
        response = self.__authenticate()
        self.__save_to_cache(response)
        return response

    def authenticate(self) -> AuthenticationResponse:
        """Authenticate with the IG REST API."""
        return self.__load_from_cache() or self.__authenticate_and_cache()
