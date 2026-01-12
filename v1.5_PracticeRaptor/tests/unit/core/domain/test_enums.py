"""Tests for domain enumerations."""
from core.domain.enums import (
    Difficulty,
    Language,
    SubmissionStatus,
    ProgressStatus,
)


class TestDifficulty:
    def test_values(self) -> None:
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.MEDIUM.value == "medium"
        assert Difficulty.HARD.value == "hard"

    def test_is_str_subclass(self) -> None:
        assert isinstance(Difficulty.EASY, str)
        assert Difficulty.EASY == "easy"

    def test_can_create_from_value(self) -> None:
        assert Difficulty("easy") == Difficulty.EASY
        assert Difficulty("medium") == Difficulty.MEDIUM


class TestLanguage:
    def test_values(self) -> None:
        assert Language.PYTHON.value == "python3"
        assert Language.GO.value == "go"
        assert Language.JAVA.value == "java"
        assert Language.JAVASCRIPT.value == "javascript"

    def test_is_str_subclass(self) -> None:
        assert isinstance(Language.PYTHON, str)
        assert Language.PYTHON == "python3"


class TestSubmissionStatus:
    def test_values(self) -> None:
        assert SubmissionStatus.ACCEPTED.value == "accepted"
        assert SubmissionStatus.WRONG_ANSWER.value == "wrong_answer"
        assert SubmissionStatus.RUNTIME_ERROR.value == "runtime_error"
        assert SubmissionStatus.TIMEOUT.value == "timeout"
        assert SubmissionStatus.MEMORY_LIMIT.value == "memory_limit"


class TestProgressStatus:
    def test_values(self) -> None:
        assert ProgressStatus.NOT_STARTED.value == "not_started"
        assert ProgressStatus.IN_PROGRESS.value == "in_progress"
        assert ProgressStatus.SOLVED.value == "solved"
