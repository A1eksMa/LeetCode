"""Tests for domain factories."""
from datetime import datetime

from core.domain.factories import (
    create_user,
    create_draft,
    create_submission,
    create_initial_progress,
)
from core.domain.enums import Language, ProgressStatus


class TestCreateUser:
    def test_creates_with_defaults(self) -> None:
        user = create_user()
        assert user.id is not None
        assert user.locale == "en"
        assert user.preferred_language == Language.PYTHON
        assert user.created_at is not None

    def test_creates_with_custom_values(self) -> None:
        user = create_user(
            user_id="custom_id",
            locale="ru",
            preferred_language=Language.GO,
        )
        assert user.id == "custom_id"
        assert user.locale == "ru"
        assert user.preferred_language == Language.GO

    def test_generates_unique_ids(self) -> None:
        user1 = create_user()
        user2 = create_user()
        assert user1.id != user2.id


class TestCreateDraft:
    def test_creates_draft(self) -> None:
        before = datetime.now()
        draft = create_draft(
            user_id="user123",
            problem_id=1,
            code="def solve(): pass",
        )
        after = datetime.now()

        assert draft.user_id == "user123"
        assert draft.problem_id == 1
        assert draft.language == Language.PYTHON
        assert draft.code == "def solve(): pass"
        assert before <= draft.updated_at <= after

    def test_creates_with_custom_language(self) -> None:
        draft = create_draft(
            user_id="user123",
            problem_id=1,
            code="func solve() {}",
            language=Language.GO,
        )
        assert draft.language == Language.GO


class TestCreateSubmission:
    def test_creates_submission(self) -> None:
        before = datetime.now()
        submission = create_submission(
            user_id="user123",
            problem_id=1,
            code="def solve(): return 42",
            execution_time_ms=10,
            memory_used_kb=1024,
        )
        after = datetime.now()

        assert submission.id is not None
        assert submission.user_id == "user123"
        assert submission.problem_id == 1
        assert submission.execution_time_ms == 10
        assert submission.memory_used_kb == 1024
        assert before <= submission.created_at <= after

    def test_generates_unique_ids(self) -> None:
        s1 = create_submission("u1", 1, "code", 10)
        s2 = create_submission("u1", 1, "code", 10)
        assert s1.id != s2.id


class TestCreateInitialProgress:
    def test_creates_not_started_progress(self) -> None:
        progress = create_initial_progress("user123", 1)

        assert progress.user_id == "user123"
        assert progress.problem_id == 1
        assert progress.status == ProgressStatus.NOT_STARTED
        assert progress.attempts == 0
        assert progress.solved_languages == ()
        assert progress.first_solved_at is None
