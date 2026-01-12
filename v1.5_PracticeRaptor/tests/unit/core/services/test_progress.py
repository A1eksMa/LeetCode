"""Tests for progress service functions."""
import pytest
from datetime import datetime
from unittest.mock import Mock

from core.domain.models import Progress
from core.domain.enums import Difficulty, Language, ProgressStatus
from core.domain.result import Ok, Err
from core.domain.errors import NotFoundError
from core.services.progress import (
    get_user_progress,
    update_progress_on_attempt,
    calculate_user_stats,
    calculate_stats_by_difficulty,
)


def make_progress(
    user_id: str = "user1",
    problem_id: int = 1,
    status: ProgressStatus = ProgressStatus.NOT_STARTED,
    attempts: int = 0,
    solved_languages: tuple[Language, ...] = (),
    first_solved_at: datetime | None = None,
) -> Progress:
    """Create a test progress entry."""
    return Progress(
        user_id=user_id,
        problem_id=problem_id,
        status=status,
        attempts=attempts,
        solved_languages=solved_languages,
        first_solved_at=first_solved_at,
    )


class TestGetUserProgress:
    """Tests for get_user_progress function."""

    def test_returns_existing_progress(self) -> None:
        """Return existing progress from repository."""
        progress = make_progress(status=ProgressStatus.IN_PROGRESS, attempts=3)
        repo = Mock()
        repo.get.return_value = Ok(progress)

        result = get_user_progress("user1", 1, repo)

        assert result == progress
        repo.get.assert_called_once_with("user1", 1)

    def test_returns_initial_progress_when_not_found(self) -> None:
        """Return initial progress when not found in repository."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Progress", id="user1:1"))

        result = get_user_progress("user1", 1, repo)

        assert result.user_id == "user1"
        assert result.problem_id == 1
        assert result.status == ProgressStatus.NOT_STARTED
        assert result.attempts == 0
        assert result.solved_languages == ()

    def test_initial_progress_has_no_solved_at(self) -> None:
        """Initial progress should have no first_solved_at."""
        repo = Mock()
        repo.get.return_value = Err(NotFoundError(entity="Progress", id="test"))

        result = get_user_progress("user1", 1, repo)

        assert result.first_solved_at is None


class TestUpdateProgressOnAttempt:
    """Tests for update_progress_on_attempt function."""

    def test_increments_attempts_on_failure(self) -> None:
        """Increment attempts when solution fails."""
        progress = make_progress(attempts=2)

        result = update_progress_on_attempt(progress, solved=False, language=Language.PYTHON)

        assert result.attempts == 3

    def test_increments_attempts_on_success(self) -> None:
        """Increment attempts when solution succeeds."""
        progress = make_progress(attempts=2)

        result = update_progress_on_attempt(progress, solved=True, language=Language.PYTHON)

        assert result.attempts == 3

    def test_sets_in_progress_on_first_failure(self) -> None:
        """Set status to IN_PROGRESS on first failed attempt."""
        progress = make_progress(status=ProgressStatus.NOT_STARTED)

        result = update_progress_on_attempt(progress, solved=False, language=Language.PYTHON)

        assert result.status == ProgressStatus.IN_PROGRESS

    def test_keeps_in_progress_on_subsequent_failures(self) -> None:
        """Keep status as IN_PROGRESS on subsequent failures."""
        progress = make_progress(status=ProgressStatus.IN_PROGRESS, attempts=5)

        result = update_progress_on_attempt(progress, solved=False, language=Language.PYTHON)

        assert result.status == ProgressStatus.IN_PROGRESS

    def test_sets_solved_on_success(self) -> None:
        """Set status to SOLVED on success."""
        progress = make_progress(status=ProgressStatus.IN_PROGRESS)

        result = update_progress_on_attempt(progress, solved=True, language=Language.PYTHON)

        assert result.status == ProgressStatus.SOLVED

    def test_adds_solved_language(self) -> None:
        """Add language to solved_languages on success."""
        progress = make_progress()

        result = update_progress_on_attempt(progress, solved=True, language=Language.PYTHON)

        assert Language.PYTHON in result.solved_languages

    def test_does_not_duplicate_solved_language(self) -> None:
        """Do not duplicate language in solved_languages."""
        progress = make_progress(
            status=ProgressStatus.SOLVED,
            solved_languages=(Language.PYTHON,),
        )

        result = update_progress_on_attempt(progress, solved=True, language=Language.PYTHON)

        assert result.solved_languages.count(Language.PYTHON) == 1

    def test_adds_new_language_to_existing(self) -> None:
        """Add new language to existing solved languages."""
        progress = make_progress(
            status=ProgressStatus.SOLVED,
            solved_languages=(Language.PYTHON,),
        )

        result = update_progress_on_attempt(progress, solved=True, language=Language.GO)

        assert Language.PYTHON in result.solved_languages
        assert Language.GO in result.solved_languages

    def test_sets_first_solved_at_on_first_success(self) -> None:
        """Set first_solved_at on first success."""
        progress = make_progress()

        result = update_progress_on_attempt(progress, solved=True, language=Language.PYTHON)

        assert result.first_solved_at is not None

    def test_preserves_first_solved_at_on_subsequent_success(self) -> None:
        """Preserve first_solved_at on subsequent successes."""
        original_time = datetime(2024, 1, 1, 12, 0, 0)
        progress = make_progress(
            status=ProgressStatus.SOLVED,
            solved_languages=(Language.PYTHON,),
            first_solved_at=original_time,
        )

        result = update_progress_on_attempt(progress, solved=True, language=Language.GO)

        assert result.first_solved_at == original_time

    def test_keeps_solved_status_on_failure(self) -> None:
        """Keep SOLVED status even when new attempt fails."""
        progress = make_progress(
            status=ProgressStatus.SOLVED,
            solved_languages=(Language.PYTHON,),
        )

        result = update_progress_on_attempt(progress, solved=False, language=Language.GO)

        assert result.status == ProgressStatus.SOLVED

    def test_is_immutable(self) -> None:
        """Original progress should not be modified."""
        progress = make_progress(attempts=2)

        result = update_progress_on_attempt(progress, solved=True, language=Language.PYTHON)

        assert progress.attempts == 2
        assert result.attempts == 3


class TestCalculateUserStats:
    """Tests for calculate_user_stats function."""

    def test_counts_solved_problems(self) -> None:
        """Count solved problems correctly."""
        all_progress = (
            make_progress(problem_id=1, status=ProgressStatus.SOLVED, attempts=2),
            make_progress(problem_id=2, status=ProgressStatus.SOLVED, attempts=1),
            make_progress(problem_id=3, status=ProgressStatus.IN_PROGRESS, attempts=5),
        )
        repo = Mock()
        repo.get_all_for_user.return_value = all_progress

        result = calculate_user_stats("user1", repo)

        assert result["total_solved"] == 2

    def test_counts_in_progress_problems(self) -> None:
        """Count in-progress problems correctly."""
        all_progress = (
            make_progress(problem_id=1, status=ProgressStatus.SOLVED),
            make_progress(problem_id=2, status=ProgressStatus.IN_PROGRESS),
            make_progress(problem_id=3, status=ProgressStatus.IN_PROGRESS),
        )
        repo = Mock()
        repo.get_all_for_user.return_value = all_progress

        result = calculate_user_stats("user1", repo)

        assert result["in_progress"] == 2

    def test_sums_total_attempts(self) -> None:
        """Sum total attempts across all problems."""
        all_progress = (
            make_progress(problem_id=1, attempts=3),
            make_progress(problem_id=2, attempts=7),
            make_progress(problem_id=3, attempts=2),
        )
        repo = Mock()
        repo.get_all_for_user.return_value = all_progress

        result = calculate_user_stats("user1", repo)

        assert result["total_attempts"] == 12

    def test_returns_zeros_for_no_progress(self) -> None:
        """Return zeros when no progress exists."""
        repo = Mock()
        repo.get_all_for_user.return_value = ()

        result = calculate_user_stats("user1", repo)

        assert result["total_solved"] == 0
        assert result["in_progress"] == 0
        assert result["total_attempts"] == 0


class TestCalculateStatsByDifficulty:
    """Tests for calculate_stats_by_difficulty function."""

    def test_groups_by_difficulty(self) -> None:
        """Group stats by difficulty correctly."""
        all_progress = (
            make_progress(problem_id=1, status=ProgressStatus.SOLVED),
            make_progress(problem_id=2, status=ProgressStatus.SOLVED),
            make_progress(problem_id=3, status=ProgressStatus.IN_PROGRESS),
        )
        difficulties = {
            1: Difficulty.EASY,
            2: Difficulty.MEDIUM,
            3: Difficulty.EASY,
        }
        repo = Mock()
        repo.get_all_for_user.return_value = all_progress

        result = calculate_stats_by_difficulty("user1", repo, difficulties)

        assert result[Difficulty.EASY]["solved"] == 1
        assert result[Difficulty.EASY]["total"] == 2
        assert result[Difficulty.MEDIUM]["solved"] == 1
        assert result[Difficulty.MEDIUM]["total"] == 1

    def test_initializes_all_difficulties(self) -> None:
        """Initialize stats for all difficulties."""
        repo = Mock()
        repo.get_all_for_user.return_value = ()

        result = calculate_stats_by_difficulty("user1", repo, {})

        assert Difficulty.EASY in result
        assert Difficulty.MEDIUM in result
        assert Difficulty.HARD in result

    def test_ignores_unknown_problem_ids(self) -> None:
        """Ignore progress for problems not in difficulties map."""
        all_progress = (
            make_progress(problem_id=1, status=ProgressStatus.SOLVED),
            make_progress(problem_id=999, status=ProgressStatus.SOLVED),
        )
        difficulties = {1: Difficulty.EASY}
        repo = Mock()
        repo.get_all_for_user.return_value = all_progress

        result = calculate_stats_by_difficulty("user1", repo, difficulties)

        assert result[Difficulty.EASY]["total"] == 1
        assert result[Difficulty.EASY]["solved"] == 1
