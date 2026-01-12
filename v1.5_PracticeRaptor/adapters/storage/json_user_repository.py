"""JSON implementation of IUserRepository."""
from pathlib import Path
from datetime import datetime
from typing import Any

from core.domain.models import User
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError

from .json_base import JsonStorageBase


class JsonUserRepository(JsonStorageBase[User]):
    """JSON file-based user repository."""

    def __init__(self, users_path: Path):
        super().__init__(users_path)

    def _user_file(self, user_id: str) -> Path:
        return self.base_path / f"{user_id}.json"

    def _parse_user(self, data: dict[str, Any]) -> User:
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        return User(
            id=data["id"],
            locale=data.get("locale", "en"),
            preferred_language=Language(data.get("preferred_language", "python3")),
            created_at=created_at,
        )

    def _serialize_user(self, user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "locale": user.locale,
            "preferred_language": user.preferred_language.value,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def get_by_id(self, user_id: str) -> Result[User, NotFoundError]:
        """Get user by ID."""
        result = self._read_json(self._user_file(user_id))
        if result.is_ok():
            return Ok(self._parse_user(result.unwrap()))
        return Err(NotFoundError(
            entity="User",
            id=user_id,
        ))

    def save(self, user: User) -> Result[User, StorageError]:
        """Save user."""
        data = self._serialize_user(user)
        result = self._write_json(self._user_file(user.id), data)
        if result.is_ok():
            return Ok(user)
        return Err(result.error)

    def delete(self, user_id: str) -> Result[None, NotFoundError]:
        """Delete user."""
        return self._delete_file(self._user_file(user_id))
