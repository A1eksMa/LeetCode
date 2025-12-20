"""Anonymous authentication provider for CLI."""
from datetime import datetime
from typing import Any
from uuid import uuid4

from core.domain.models import User
from core.domain.enums import Language
from core.domain.result import Ok, Result
from core.ports.auth import IAuthProvider, AuthError


class AnonymousAuthProvider:
    """
    Authentication provider for anonymous/local users.

    Used in CLI mode where no real authentication is needed.
    Creates a local user with a persistent ID stored in config.
    """

    def __init__(self, user_id: str | None = None):
        """
        Initialize with optional fixed user ID.

        Args:
            user_id: Fixed user ID. If None, generates a new one.
        """
        self._user_id = user_id or f"local_{uuid4().hex[:8]}"
        self._user: User | None = None

    def get_current_user(self) -> Result[User, AuthError]:
        """Get the local anonymous user."""
        if self._user is None:
            self._user = User(
                id=self._user_id,
                locale="en",
                preferred_language=Language.PYTHON,
                created_at=datetime.now(),
            )
        return Ok(self._user)

    def authenticate(self, credentials: dict[str, Any]) -> Result[User, AuthError]:
        """
        Authenticate with credentials.

        For anonymous auth, this just returns the current user.
        Credentials are ignored.
        """
        return self.get_current_user()
