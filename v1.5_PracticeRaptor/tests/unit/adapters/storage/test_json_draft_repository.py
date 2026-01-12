"""Tests for JsonDraftRepository."""
import pytest
from pathlib import Path
from datetime import datetime

from adapters.storage.json_draft_repository import JsonDraftRepository
from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.factories import create_draft


class TestJsonDraftRepository:
    """Tests for JsonDraftRepository."""

    def test_save_and_get(self, tmp_path: Path) -> None:
        """Test saving and retrieving a draft."""
        repo = JsonDraftRepository(tmp_path)
        draft = create_draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="def solution(): pass",
        )

        save_result = repo.save(draft)
        assert save_result.is_ok()

        get_result = repo.get("user_123", 1, Language.PYTHON)
        assert get_result.is_ok()

        retrieved = get_result.unwrap()
        assert retrieved.user_id == "user_123"
        assert retrieved.problem_id == 1
        assert retrieved.language == Language.PYTHON
        assert retrieved.code == "def solution(): pass"

    def test_get_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that getting a missing draft returns an error."""
        repo = JsonDraftRepository(tmp_path)

        result = repo.get("user_123", 1, Language.PYTHON)

        assert result.is_err()
        assert result.error.entity == "Draft"

    def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        """Test that saving overwrites existing draft."""
        repo = JsonDraftRepository(tmp_path)
        draft = create_draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="original code",
        )
        repo.save(draft)

        updated_draft = Draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="updated code",
            updated_at=datetime.now(),
        )
        repo.save(updated_draft)

        result = repo.get("user_123", 1, Language.PYTHON)
        assert result.is_ok()
        assert result.unwrap().code == "updated code"

    def test_delete_removes_draft(self, tmp_path: Path) -> None:
        """Test deleting a draft."""
        repo = JsonDraftRepository(tmp_path)
        draft = create_draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="code",
        )
        repo.save(draft)

        delete_result = repo.delete("user_123", 1, Language.PYTHON)
        assert delete_result.is_ok()

        get_result = repo.get("user_123", 1, Language.PYTHON)
        assert get_result.is_err()

    def test_delete_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that deleting a missing draft returns an error."""
        repo = JsonDraftRepository(tmp_path)

        result = repo.delete("user_123", 1, Language.PYTHON)

        assert result.is_err()

    def test_get_all_for_user_returns_all_drafts(self, tmp_path: Path) -> None:
        """Test getting all drafts for a user."""
        repo = JsonDraftRepository(tmp_path)
        draft1 = create_draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="code1",
        )
        draft2 = create_draft(
            user_id="user_123",
            problem_id=2,
            language=Language.PYTHON,
            code="code2",
        )
        draft3 = create_draft(
            user_id="other_user",
            problem_id=1,
            language=Language.PYTHON,
            code="other",
        )
        repo.save(draft1)
        repo.save(draft2)
        repo.save(draft3)

        drafts = repo.get_all_for_user("user_123")

        assert len(drafts) == 2
        user_problem_ids = {d.problem_id for d in drafts}
        assert user_problem_ids == {1, 2}

    def test_get_all_for_user_returns_empty_for_no_drafts(
        self, tmp_path: Path
    ) -> None:
        """Test that get_all_for_user returns empty tuple for no drafts."""
        repo = JsonDraftRepository(tmp_path)

        drafts = repo.get_all_for_user("nonexistent")

        assert drafts == ()

    def test_separate_drafts_per_language(self, tmp_path: Path) -> None:
        """Test that drafts are separate per language."""
        repo = JsonDraftRepository(tmp_path)
        python_draft = create_draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="python code",
        )
        go_draft = create_draft(
            user_id="user_123",
            problem_id=1,
            language=Language.GO,
            code="go code",
        )
        repo.save(python_draft)
        repo.save(go_draft)

        python_result = repo.get("user_123", 1, Language.PYTHON)
        go_result = repo.get("user_123", 1, Language.GO)

        assert python_result.is_ok()
        assert go_result.is_ok()
        assert python_result.unwrap().code == "python code"
        assert go_result.unwrap().code == "go code"

    def test_drafts_sorted_by_updated_at_descending(self, tmp_path: Path) -> None:
        """Test that drafts are sorted by updated_at descending."""
        repo = JsonDraftRepository(tmp_path)
        older = Draft(
            user_id="user_123",
            problem_id=1,
            language=Language.PYTHON,
            code="old",
            updated_at=datetime(2024, 1, 1),
        )
        newer = Draft(
            user_id="user_123",
            problem_id=2,
            language=Language.PYTHON,
            code="new",
            updated_at=datetime(2024, 6, 1),
        )
        repo.save(older)
        repo.save(newer)

        drafts = repo.get_all_for_user("user_123")

        assert len(drafts) == 2
        assert drafts[0].problem_id == 2  # Newer first
        assert drafts[1].problem_id == 1  # Older second
