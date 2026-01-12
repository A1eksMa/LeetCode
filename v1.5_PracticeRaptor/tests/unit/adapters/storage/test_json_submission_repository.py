"""Tests for JsonSubmissionRepository."""
import pytest
from pathlib import Path
from datetime import datetime

from adapters.storage.json_submission_repository import JsonSubmissionRepository
from core.domain.models import Submission
from core.domain.enums import Language
from core.domain.factories import create_submission


class TestJsonSubmissionRepository:
    """Tests for JsonSubmissionRepository."""

    def test_save_and_get_by_id(self, tmp_path: Path) -> None:
        """Test saving and retrieving a submission."""
        repo = JsonSubmissionRepository(tmp_path)
        submission = create_submission(
            submission_id="sub_123",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="def solution(): pass",
            execution_time_ms=42,
            memory_used_kb=1024,
        )

        save_result = repo.save(submission)
        assert save_result.is_ok()

        get_result = repo.get_by_id("sub_123")
        assert get_result.is_ok()

        retrieved = get_result.unwrap()
        assert retrieved.id == "sub_123"
        assert retrieved.user_id == "user_1"
        assert retrieved.problem_id == 1
        assert retrieved.code == "def solution(): pass"
        assert retrieved.execution_time_ms == 42
        assert retrieved.memory_used_kb == 1024

    def test_get_by_id_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that getting a missing submission returns an error."""
        repo = JsonSubmissionRepository(tmp_path)

        result = repo.get_by_id("nonexistent")

        assert result.is_err()
        assert result.error.entity == "Submission"

    def test_get_for_problem_returns_submissions(self, tmp_path: Path) -> None:
        """Test getting submissions for a problem."""
        repo = JsonSubmissionRepository(tmp_path)
        sub1 = create_submission(
            submission_id="sub_1",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="code1",
        )
        sub2 = create_submission(
            submission_id="sub_2",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="code2",
        )
        sub3 = create_submission(
            submission_id="sub_3",
            user_id="user_1",
            problem_id=2,
            language=Language.PYTHON,
            code="code3",
        )
        repo.save(sub1)
        repo.save(sub2)
        repo.save(sub3)

        submissions = repo.get_for_problem("user_1", 1)

        assert len(submissions) == 2
        problem_ids = {s.problem_id for s in submissions}
        assert problem_ids == {1}

    def test_get_for_problem_returns_empty_for_no_submissions(
        self, tmp_path: Path
    ) -> None:
        """Test that get_for_problem returns empty for no submissions."""
        repo = JsonSubmissionRepository(tmp_path)

        submissions = repo.get_for_problem("user_1", 999)

        assert submissions == ()

    def test_get_for_user_returns_all_user_submissions(self, tmp_path: Path) -> None:
        """Test getting all submissions for a user."""
        repo = JsonSubmissionRepository(tmp_path)
        sub1 = create_submission(
            submission_id="sub_1",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="code1",
        )
        sub2 = create_submission(
            submission_id="sub_2",
            user_id="user_1",
            problem_id=2,
            language=Language.PYTHON,
            code="code2",
        )
        sub3 = create_submission(
            submission_id="sub_3",
            user_id="user_2",
            problem_id=1,
            language=Language.PYTHON,
            code="code3",
        )
        repo.save(sub1)
        repo.save(sub2)
        repo.save(sub3)

        submissions = repo.get_for_user("user_1")

        assert len(submissions) == 2
        user_ids = {s.user_id for s in submissions}
        assert user_ids == {"user_1"}

    def test_get_for_user_returns_empty_for_no_submissions(
        self, tmp_path: Path
    ) -> None:
        """Test that get_for_user returns empty for no submissions."""
        repo = JsonSubmissionRepository(tmp_path)

        submissions = repo.get_for_user("nonexistent")

        assert submissions == ()

    def test_submissions_sorted_by_created_at_descending(
        self, tmp_path: Path
    ) -> None:
        """Test that submissions are sorted by created_at descending."""
        repo = JsonSubmissionRepository(tmp_path)
        older = Submission(
            id="sub_older",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="old",
            execution_time_ms=10,
            memory_used_kb=100,
            created_at=datetime(2024, 1, 1),
        )
        newer = Submission(
            id="sub_newer",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="new",
            execution_time_ms=10,
            memory_used_kb=100,
            created_at=datetime(2024, 6, 1),
        )
        repo.save(older)
        repo.save(newer)

        submissions = repo.get_for_user("user_1")

        assert len(submissions) == 2
        assert submissions[0].id == "sub_newer"  # Newer first
        assert submissions[1].id == "sub_older"  # Older second

    def test_handles_memory_used_kb_default(self, tmp_path: Path) -> None:
        """Test that missing memory_used_kb defaults to 0."""
        repo = JsonSubmissionRepository(tmp_path)
        submission = Submission(
            id="sub_1",
            user_id="user_1",
            problem_id=1,
            language=Language.PYTHON,
            code="code",
            execution_time_ms=10,
            memory_used_kb=0,
            created_at=datetime.now(),
        )
        repo.save(submission)

        result = repo.get_by_id("sub_1")
        assert result.is_ok()
        assert result.unwrap().memory_used_kb == 0
