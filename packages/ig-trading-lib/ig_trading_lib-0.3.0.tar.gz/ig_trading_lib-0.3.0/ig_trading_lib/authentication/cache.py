import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from .models import AuthenticationResponse


logger = logging.getLogger(__name__)


class AuthenticationCacheABC(ABC):
    """Abstract base class for authentication response caching."""

    @staticmethod
    @abstractmethod
    def save_authentication_response(response: AuthenticationResponse) -> None:
        raise NotImplementedError("Implement Authorization response caching!")

    @staticmethod
    @abstractmethod
    def load_authentication_response() -> Optional[AuthenticationResponse]:
        raise NotImplementedError("Implement Authorization response loading!")


class DurableCache(AuthenticationCacheABC):
    """Local storage for tokens using a file, with optional encryption."""

    def __init__(self, path: str, encryption_key: Optional[bytes] = None) -> None:
        """Initializes token storage with a file path and an optional encryption key.
        :param path: Path to the file where tokens will be stored including the file name and extension.
        :param encryption_key: Optional encryption key for securing tokens. Encryption is disabled if not provided.
        """
        self.path = Path(path)
        self.fernet = Fernet(encryption_key) if encryption_key else None
        logger.info(
            "Authentication cache initialized. Encryption %s.",
            "enabled" if self.fernet else "disabled",
        )

    def save_authentication_response(self, response: AuthenticationResponse) -> None:
        """Save the authentication response to the cache.
        :param response: The authentication response to be cached.
        """
        data = response.model_dump()
        try:
            data_bytes = json.dumps(data).encode()
            if self.fernet:
                encrypted_data = self.fernet.encrypt(data_bytes)
                self.path.write_bytes(encrypted_data)
            else:
                self.path.write_text(json.dumps(data, indent=4))
        except PermissionError:
            logger.error(
                "Permission denied: Unable to cache authentication response to %s",
                str(self.path.absolute()),
            )
        except TypeError as e:
            logger.error("TypeError encountered during caching: %s", str(e))
        except OSError as e:
            logger.error(
                "Failed to cache authentication response due to an OS error: %s", str(e)
            )

    def load_authentication_response(self) -> Optional[AuthenticationResponse]:
        """Load the authentication response from the cache if it exists.
        :return: The authentication response if it exists, otherwise None."""
        if not self.path.exists():
            logger.warning("Authentication cache file not found: %s", self.path)
            return None
        try:
            if self.fernet:
                encrypted_data = self.path.read_bytes()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                data = json.loads(decrypted_data)
            else:
                data = json.loads(self.path.read_text())
            return AuthenticationResponse.model_validate(data)
        except PermissionError:
            logger.error(
                "Permission denied: Unable to load authentication response from %s",
                self.path,
            )
            return None
        except (json.JSONDecodeError, InvalidToken) as e:
            logger.error("Failed to load authentication response: %s", str(e))
            return None
        except OSError as e:
            logger.error(
                "Failed to load authentication response due to an OS error: %s", str(e)
            )
            return None


class InMemoryCache(AuthenticationCacheABC):
    """In-memory storage for authentication response."""

    def __init__(self) -> None:
        self.response = None
        logger.info("In-memory cache initialized.")

    def save_authentication_response(self, response: AuthenticationResponse) -> None:
        """Save the authentication response to the cache if it exists.
        :param response: The authentication response to be cached."""
        self.response = response

    def load_authentication_response(self) -> Optional[AuthenticationResponse]:
        """Load the authentication response from memory if it exists.
        :return: The authentication response if it exists, otherwise None."""
        if self.response:
            return self.response
        else:
            return None
