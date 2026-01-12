"""JSON implementation of IDraftRepository."""
from pathlib import Path
from datetime import datetime
from typing import Any

from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError

from .json_base import JsonStorageBase


class JsonDraftRepository(JsonStorageBase[Draft]):
    """JSON file-based draft repository."""

    def __init__(self, drafts_path: Path):
        super().__init__(drafts_path)

    def _draft_file(self, user_id: str, problem_id: int, language: Language) -> Path:
        return self.base_path / user_id / f"{problem_id}_{language.value}.json"

    def _parse_draft(self, data: dict[str, Any]) -> Draft:
        return Draft(
            user_id=data["user_id"],
            problem_id=data["problem_id"],
            language=Language(data["language"]),
            code=data["code"],
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def _serialize_draft(self, draft: Draft) -> dict[str, Any]:
        return {
            "user_id": draft.user_id,
            "problem_id": draft.problem_id,
            "language": draft.language.value,
            "code": draft.code,
            "updated_at": draft.updated_at.isoformat(),
        }

    def get(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[Draft, NotFoundError]:
        """Get draft."""
        file_path = self._draft_file(user_id, problem_id, language)
        result = self._read_json(file_path)
        if result.is_ok():
            return Ok(self._parse_draft(result.unwrap()))
        return Err(NotFoundError(
            entity="Draft",
            id=f"{user_id}/{problem_id}/{language.value}",
        ))

    def save(self, draft: Draft) -> Result[Draft, StorageError]:
        """Save draft."""
        file_path = self._draft_file(draft.user_id, draft.problem_id, draft.language)
        data = self._serialize_draft(draft)
        result = self._write_json(file_path, data)
        if result.is_ok():
            return Ok(draft)
        return Err(result.error)

    def delete(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[None, NotFoundError]:
        """Delete draft."""
        file_path = self._draft_file(user_id, problem_id, language)
        return self._delete_file(file_path)

    def get_all_for_user(self, user_id: str) -> tuple[Draft, ...]:
        """Get all drafts for user."""
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return ()

        drafts: list[Draft] = []
        for file_path in user_dir.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                drafts.append(self._parse_draft(result.unwrap()))

        return tuple(sorted(drafts, key=lambda d: d.updated_at, reverse=True))
