"""JSON implementation of ISubmissionRepository."""
from pathlib import Path
from datetime import datetime
from typing import Any

from core.domain.models import Submission
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError

from .json_base import JsonStorageBase


class JsonSubmissionRepository(JsonStorageBase[Submission]):
    """JSON file-based submission repository."""

    def __init__(self, submissions_path: Path):
        super().__init__(submissions_path)

    def _user_dir(self, user_id: str) -> Path:
        return self.base_path / user_id

    def _parse_submission(self, data: dict[str, Any]) -> Submission:
        return Submission(
            id=data["id"],
            user_id=data["user_id"],
            problem_id=data["problem_id"],
            language=Language(data["language"]),
            code=data["code"],
            execution_time_ms=data["execution_time_ms"],
            memory_used_kb=data.get("memory_used_kb", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def _serialize_submission(self, submission: Submission) -> dict[str, Any]:
        return {
            "id": submission.id,
            "user_id": submission.user_id,
            "problem_id": submission.problem_id,
            "language": submission.language.value,
            "code": submission.code,
            "execution_time_ms": submission.execution_time_ms,
            "memory_used_kb": submission.memory_used_kb,
            "created_at": submission.created_at.isoformat(),
        }

    def get_by_id(self, submission_id: str) -> Result[Submission, NotFoundError]:
        """Get submission by ID."""
        # Search in all user directories
        for user_dir in self.base_path.iterdir():
            if user_dir.is_dir():
                file_path = user_dir / f"{submission_id}.json"
                if file_path.exists():
                    result = self._read_json(file_path)
                    if result.is_ok():
                        return Ok(self._parse_submission(result.unwrap()))

        return Err(NotFoundError(
            entity="Submission",
            id=submission_id,
        ))

    def save(self, submission: Submission) -> Result[Submission, StorageError]:
        """Save new submission."""
        user_dir = self._user_dir(submission.user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        file_path = user_dir / f"{submission.id}.json"
        data = self._serialize_submission(submission)

        result = self._write_json(file_path, data)
        if result.is_ok():
            return Ok(submission)
        return Err(result.error)

    def get_for_problem(
        self,
        user_id: str,
        problem_id: int,
    ) -> tuple[Submission, ...]:
        """Get all submissions for user/problem."""
        user_dir = self._user_dir(user_id)
        if not user_dir.exists():
            return ()

        submissions: list[Submission] = []
        for file_path in user_dir.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                submission = self._parse_submission(result.unwrap())
                if submission.problem_id == problem_id:
                    submissions.append(submission)

        return tuple(sorted(submissions, key=lambda s: s.created_at, reverse=True))

    def get_for_user(self, user_id: str) -> tuple[Submission, ...]:
        """Get all submissions for user."""
        user_dir = self._user_dir(user_id)
        if not user_dir.exists():
            return ()

        submissions: list[Submission] = []
        for file_path in user_dir.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                submissions.append(self._parse_submission(result.unwrap()))

        return tuple(sorted(submissions, key=lambda s: s.created_at, reverse=True))
