"""Tests for drafts service functions."""
import pytest
from datetime import datetime
from unittest.mock import Mock

from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.result import Ok, Err
from core.domain.errors import NotFoundError, StorageError
from core.services.drafts import (
    get_draft,
    save_draft,
    delete_draft,
    get_or_create_code,
)


def make_draft(
    user_id: str = "user1",
    problem_id: int = 1,
    language: Language = Language.PYTHON,
    code: str = "def solution(): pass",
    updated_at: datetime | None = None,
) -> Draft:
    """Create a test draft."""
    return Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=updated_at or datetime.now(),
    )


class TestGetDraft:
    """Tests for get_draft function."""

    def test_returns_draft_when_found(self) -> None:
        """Return draft when repository finds it."""
        draft = make_draft(code="def solution(x): return x * 2")
        repo = Mock()
        repo.get.return_value = Ok(draft)

        result = get_draft("user1", 1, Language.PYTHON, repo)

        assert result.is_ok()
        assert result.unwrap() == draft
        repo.get.assert_called_once_with("user1", 1, Language.PYTHON)

    def test_returns_error_when_not_found(self) -> None:
        """Return error when draft not found."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Draft", id="user1:1"))

        result = get_draft("user1", 1, Language.PYTHON, repo)

        assert result.is_err()
        assert isinstance(result.error, NotFoundError)

    def test_handles_different_languages(self) -> None:
        """Handle different language parameters."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Draft", id="test"))

        get_draft("user1", 1, Language.GO, repo)

        repo.get.assert_called_once_with("user1", 1, Language.GO)


class TestSaveDraft:
    """Tests for save_draft function."""

    def test_saves_draft_successfully(self) -> None:
        """Save draft and return it."""
        repo = Mock()
        repo.save.side_effect = lambda d: Ok(d)

        result = save_draft(
            user_id="user1",
            problem_id=1,
            language=Language.PYTHON,
            code="def solution(): return 42",
            draft_repo=repo,
        )

        assert result.is_ok()
        saved_draft = result.unwrap()
        assert saved_draft.user_id == "user1"
        assert saved_draft.problem_id == 1
        assert saved_draft.language == Language.PYTHON
        assert saved_draft.code == "def solution(): return 42"

    def test_returns_storage_error(self) -> None:
        """Return error when storage fails."""
        repo = Mock()
        repo.save.return_value = Err(StorageError(message="Write failed", operation="write"))

        result = save_draft("user1", 1, Language.PYTHON, "code", repo)

        assert result.is_err()
        assert isinstance(result.error, StorageError)

    def test_sets_updated_at(self) -> None:
        """Set updated_at to current time."""
        repo = Mock()
        repo.save.side_effect = lambda d: Ok(d)
        before = datetime.now()

        result = save_draft("user1", 1, Language.PYTHON, "code", repo)

        after = datetime.now()
        assert result.is_ok()
        assert before <= result.unwrap().updated_at <= after


class TestDeleteDraft:
    """Tests for delete_draft function."""

    def test_deletes_draft_successfully(self) -> None:
        """Delete draft and return None."""
        repo = Mock()
        repo.delete.return_value = Ok(None)

        result = delete_draft("user1", 1, Language.PYTHON, repo)

        assert result.is_ok()
        repo.delete.assert_called_once_with("user1", 1, Language.PYTHON)

    def test_returns_error_when_not_found(self) -> None:
        """Return error when draft to delete not found."""
        repo = Mock()
        repo.delete.return_value = Err(NotFoundError(entity="Draft", id="user1:1"))

        result = delete_draft("user1", 1, Language.PYTHON, repo)

        assert result.is_err()
        assert isinstance(result.error, NotFoundError)


class TestGetOrCreateCode:
    """Tests for get_or_create_code function."""

    def test_returns_existing_draft_code(self) -> None:
        """Return code from existing draft."""
        existing_code = "def two_sum(nums, target):\n    # My solution\n    pass"
        draft = make_draft(code=existing_code)
        repo = Mock()
        repo.get.return_value = Ok(draft)

        result = get_or_create_code(
            user_id="user1",
            problem_id=1,
            language=Language.PYTHON,
            signature="def two_sum(nums, target):",
            draft_repo=repo,
        )

        assert result == existing_code

    def test_returns_template_when_no_draft(self) -> None:
        """Return template with signature when no draft exists."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Draft", id="test"))

        result = get_or_create_code(
            user_id="user1",
            problem_id=1,
            language=Language.PYTHON,
            signature="def two_sum(nums, target):",
            draft_repo=repo,
        )

        assert result == "def two_sum(nums, target):\n    pass"

    def test_template_uses_provided_signature(self) -> None:
        """Template uses the exact provided signature."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Draft", id="test"))

        result = get_or_create_code(
            user_id="user1",
            problem_id=1,
            language=Language.PYTHON,
            signature="def solve(x: int) -> int:",
            draft_repo=repo,
        )

        assert result.startswith("def solve(x: int) -> int:")

    def test_handles_different_languages(self) -> None:
        """Handle different languages when getting draft."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Draft", id="test"))

        get_or_create_code("user1", 1, Language.GO, "func solve()", repo)

        repo.get.assert_called_once_with("user1", 1, Language.GO)
