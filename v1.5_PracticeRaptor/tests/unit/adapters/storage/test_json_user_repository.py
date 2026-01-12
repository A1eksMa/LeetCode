"""Tests for JsonUserRepository."""
import pytest
from pathlib import Path
from datetime import datetime

from adapters.storage.json_user_repository import JsonUserRepository
from core.domain.models import User
from core.domain.enums import Language
from core.domain.factories import create_user


class TestJsonUserRepository:
    """Tests for JsonUserRepository."""

    def test_save_and_get_by_id(self, tmp_path: Path) -> None:
        """Test saving and retrieving a user."""
        repo = JsonUserRepository(tmp_path)
        user = create_user(
            user_id="user_123",
            locale="ru",
            preferred_language=Language.PYTHON,
        )

        save_result = repo.save(user)
        assert save_result.is_ok()

        get_result = repo.get_by_id("user_123")
        assert get_result.is_ok()

        retrieved = get_result.unwrap()
        assert retrieved.id == "user_123"
        assert retrieved.locale == "ru"
        assert retrieved.preferred_language == Language.PYTHON

    def test_get_by_id_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that getting a missing user returns an error."""
        repo = JsonUserRepository(tmp_path)

        result = repo.get_by_id("nonexistent")

        assert result.is_err()
        assert result.error.entity == "User"

    def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        """Test that saving overwrites existing user."""
        repo = JsonUserRepository(tmp_path)
        user = create_user(user_id="user_123", locale="en")
        repo.save(user)

        updated_user = User(
            id="user_123",
            locale="ru",
            preferred_language=Language.GO,
            created_at=user.created_at,
        )
        repo.save(updated_user)

        result = repo.get_by_id("user_123")
        assert result.is_ok()
        assert result.unwrap().locale == "ru"
        assert result.unwrap().preferred_language == Language.GO

    def test_delete_removes_user(self, tmp_path: Path) -> None:
        """Test deleting a user."""
        repo = JsonUserRepository(tmp_path)
        user = create_user(user_id="user_123")
        repo.save(user)

        delete_result = repo.delete("user_123")
        assert delete_result.is_ok()

        get_result = repo.get_by_id("user_123")
        assert get_result.is_err()

    def test_delete_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that deleting a missing user returns an error."""
        repo = JsonUserRepository(tmp_path)

        result = repo.delete("nonexistent")

        assert result.is_err()

    def test_preserves_created_at(self, tmp_path: Path) -> None:
        """Test that created_at is preserved."""
        repo = JsonUserRepository(tmp_path)
        created = datetime(2024, 1, 15, 10, 30, 0)
        user = User(
            id="user_123",
            locale="en",
            preferred_language=Language.PYTHON,
            created_at=created,
        )
        repo.save(user)

        result = repo.get_by_id("user_123")
        assert result.is_ok()
        assert result.unwrap().created_at == created

