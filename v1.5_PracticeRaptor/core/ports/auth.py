"""Authentication interfaces (Ports)."""
from typing import Protocol, Any

from core.domain.models import User
from core.domain.result import Result
from core.domain.errors import DomainError


class AuthError(DomainError):
    """Authentication/authorization error."""
    pass


class IAuthProvider(Protocol):
    """Interface for authentication."""

    def get_current_user(self) -> Result[User, AuthError]:
        """
        Get currently authenticated user.

        Returns:
            Result with User on success or AuthError if not authenticated
        """
        ...

    def authenticate(self, credentials: dict[str, Any]) -> Result[User, AuthError]:
        """
        Authenticate with credentials.

        Args:
            credentials: Authentication credentials (format depends on provider)

        Returns:
            Result with User on success or AuthError on failure
        """
        ...
