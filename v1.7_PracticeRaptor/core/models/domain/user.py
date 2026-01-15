"""User domain model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """User entity with authentication data.

    Represents a registered user account.
    Settings are stored separately in Settings entity.
    """

    user_id: int = 0
    user_name: str = ""
    hash_password: str = ""
    email: str = ""


# Default user for CLI anonymous mode
DEFAULT_USER = User(
    user_id=0,
    user_name="anonymous",
    hash_password="",
    email="",
)
