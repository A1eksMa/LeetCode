"""JSON implementation of IProgressRepository."""
from pathlib import Path
from datetime import datetime
from typing import Any

from core.domain.models import Progress
from core.domain.enums import Difficulty, Language, ProgressStatus
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError

from .json_base import JsonStorageBase


class JsonProgressRepository(JsonStorageBase[Progress]):
    """JSON file-based progress repository."""

    def __init__(self, progress_path: Path):
        super().__init__(progress_path)

    def _progress_file(self, user_id: str, problem_id: int) -> Path:
        return self.base_path / user_id / f"{problem_id}.json"

    def _parse_progress(self, data: dict[str, Any]) -> Progress:
        solved_languages = tuple(
            Language(lang) for lang in data.get("solved_languages", [])
        )
        first_solved_at = None
        if data.get("first_solved_at"):
            first_solved_at = datetime.fromisoformat(data["first_solved_at"])

        return Progress(
            user_id=data["user_id"],
            problem_id=data["problem_id"],
            status=ProgressStatus(data["status"]),
            attempts=data.get("attempts", 0),
            solved_languages=solved_languages,
            first_solved_at=first_solved_at,
        )

    def _serialize_progress(self, progress: Progress) -> dict[str, Any]:
        return {
            "user_id": progress.user_id,
            "problem_id": progress.problem_id,
            "status": progress.status.value,
            "attempts": progress.attempts,
            "solved_languages": [lang.value for lang in progress.solved_languages],
            "first_solved_at": progress.first_solved_at.isoformat()
                if progress.first_solved_at else None,
        }

    def get(
        self,
        user_id: str,
        problem_id: int,
    ) -> Result[Progress, NotFoundError]:
        """Get progress for user/problem."""
        file_path = self._progress_file(user_id, problem_id)
        result = self._read_json(file_path)
        if result.is_ok():
            return Ok(self._parse_progress(result.unwrap()))
        return Err(NotFoundError(
            entity="Progress",
            id=f"{user_id}/{problem_id}",
        ))

    def save(self, progress: Progress) -> Result[Progress, StorageError]:
        """Save progress."""
        file_path = self._progress_file(progress.user_id, progress.problem_id)
        data = self._serialize_progress(progress)
        result = self._write_json(file_path, data)
        if result.is_ok():
            return Ok(progress)
        return Err(result.error)

    def get_all_for_user(self, user_id: str) -> tuple[Progress, ...]:
        """Get all progress entries for user."""
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return ()

        progress_list: list[Progress] = []
        for file_path in user_dir.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                progress_list.append(self._parse_progress(result.unwrap()))

        return tuple(sorted(progress_list, key=lambda p: p.problem_id))

    def get_solved_count(self, user_id: str) -> int:
        """Get number of solved problems for user."""
        all_progress = self.get_all_for_user(user_id)
        return sum(1 for p in all_progress if p.status == ProgressStatus.SOLVED)

    def get_solved_by_difficulty(
        self,
        user_id: str,
    ) -> dict[Difficulty, int]:
        """
        Get solved count grouped by difficulty.

        Note: Returns empty dict - cross-aggregate queries should be
        handled at the service level where we have access to both
        progress and problem repositories.
        """
        return {d: 0 for d in Difficulty}
