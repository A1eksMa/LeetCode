"""Tests for JsonProgressRepository."""
import pytest
from pathlib import Path
from datetime import datetime

from adapters.storage.json_progress_repository import JsonProgressRepository
from core.domain.models import Progress
from core.domain.enums import Difficulty, Language, ProgressStatus
from core.domain.factories import create_progress


class TestJsonProgressRepository:
    """Tests for JsonProgressRepository."""

    def test_save_and_get(self, tmp_path: Path) -> None:
        """Test saving and retrieving progress."""
        repo = JsonProgressRepository(tmp_path)
        progress = create_progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.IN_PROGRESS,
            attempts=3,
        )

        save_result = repo.save(progress)
        assert save_result.is_ok()

        get_result = repo.get("user_123", 1)
        assert get_result.is_ok()

        retrieved = get_result.unwrap()
        assert retrieved.user_id == "user_123"
        assert retrieved.problem_id == 1
        assert retrieved.status == ProgressStatus.IN_PROGRESS
        assert retrieved.attempts == 3

    def test_get_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that getting missing progress returns an error."""
        repo = JsonProgressRepository(tmp_path)

        result = repo.get("user_123", 999)

        assert result.is_err()
        assert result.error.entity == "Progress"

    def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        """Test that saving overwrites existing progress."""
        repo = JsonProgressRepository(tmp_path)
        progress = create_progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.IN_PROGRESS,
            attempts=1,
        )
        repo.save(progress)

        updated = Progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.SOLVED,
            attempts=5,
            solved_languages=(Language.PYTHON,),
            first_solved_at=datetime.now(),
        )
        repo.save(updated)

        result = repo.get("user_123", 1)
        assert result.is_ok()
        assert result.unwrap().status == ProgressStatus.SOLVED
        assert result.unwrap().attempts == 5
        assert Language.PYTHON in result.unwrap().solved_languages

    def test_get_all_for_user_returns_all_progress(self, tmp_path: Path) -> None:
        """Test getting all progress for a user."""
        repo = JsonProgressRepository(tmp_path)
        progress1 = create_progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.SOLVED,
        )
        progress2 = create_progress(
            user_id="user_123",
            problem_id=2,
            status=ProgressStatus.IN_PROGRESS,
        )
        progress3 = create_progress(
            user_id="other_user",
            problem_id=1,
            status=ProgressStatus.SOLVED,
        )
        repo.save(progress1)
        repo.save(progress2)
        repo.save(progress3)

        all_progress = repo.get_all_for_user("user_123")

        assert len(all_progress) == 2
        problem_ids = {p.problem_id for p in all_progress}
        assert problem_ids == {1, 2}

    def test_get_all_for_user_returns_empty_for_no_progress(
        self, tmp_path: Path
    ) -> None:
        """Test that get_all_for_user returns empty for no progress."""
        repo = JsonProgressRepository(tmp_path)

        all_progress = repo.get_all_for_user("nonexistent")

        assert all_progress == ()

    def test_get_solved_count(self, tmp_path: Path) -> None:
        """Test counting solved problems."""
        repo = JsonProgressRepository(tmp_path)
        solved1 = create_progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.SOLVED,
        )
        solved2 = create_progress(
            user_id="user_123",
            problem_id=2,
            status=ProgressStatus.SOLVED,
        )
        in_progress = create_progress(
            user_id="user_123",
            problem_id=3,
            status=ProgressStatus.IN_PROGRESS,
        )
        repo.save(solved1)
        repo.save(solved2)
        repo.save(in_progress)

        count = repo.get_solved_count("user_123")

        assert count == 2

    def test_get_solved_count_returns_zero_for_no_progress(
        self, tmp_path: Path
    ) -> None:
        """Test that get_solved_count returns 0 for no progress."""
        repo = JsonProgressRepository(tmp_path)

        count = repo.get_solved_count("nonexistent")

        assert count == 0

    def test_get_solved_by_difficulty_returns_default(self, tmp_path: Path) -> None:
        """Test that get_solved_by_difficulty returns default values."""
        repo = JsonProgressRepository(tmp_path)

        result = repo.get_solved_by_difficulty("user_123")

        assert result == {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 0,
            Difficulty.HARD: 0,
        }

    def test_progress_sorted_by_problem_id(self, tmp_path: Path) -> None:
        """Test that progress entries are sorted by problem_id."""
        repo = JsonProgressRepository(tmp_path)
        progress3 = create_progress(user_id="user_123", problem_id=3)
        progress1 = create_progress(user_id="user_123", problem_id=1)
        progress2 = create_progress(user_id="user_123", problem_id=2)
        repo.save(progress3)
        repo.save(progress1)
        repo.save(progress2)

        all_progress = repo.get_all_for_user("user_123")

        assert len(all_progress) == 3
        assert all_progress[0].problem_id == 1
        assert all_progress[1].problem_id == 2
        assert all_progress[2].problem_id == 3

    def test_preserves_solved_languages(self, tmp_path: Path) -> None:
        """Test that solved_languages are preserved."""
        repo = JsonProgressRepository(tmp_path)
        progress = Progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.SOLVED,
            attempts=5,
            solved_languages=(Language.PYTHON, Language.GO),
            first_solved_at=datetime(2024, 6, 15),
        )
        repo.save(progress)

        result = repo.get("user_123", 1)
        assert result.is_ok()
        retrieved = result.unwrap()
        assert set(retrieved.solved_languages) == {Language.PYTHON, Language.GO}
        assert retrieved.first_solved_at == datetime(2024, 6, 15)

    def test_handles_progress_without_first_solved_at(self, tmp_path: Path) -> None:
        """Test handling progress without first_solved_at."""
        repo = JsonProgressRepository(tmp_path)
        progress = Progress(
            user_id="user_123",
            problem_id=1,
            status=ProgressStatus.IN_PROGRESS,
            attempts=1,
            solved_languages=(),
            first_solved_at=None,
        )
        repo.save(progress)

        result = repo.get("user_123", 1)
        assert result.is_ok()
        assert result.unwrap().first_solved_at is None
