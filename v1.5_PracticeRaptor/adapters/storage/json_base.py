"""Base utilities for JSON storage."""
import json
from pathlib import Path
from typing import TypeVar, Generic, Any

from core.domain.result import Ok, Err, Result
from core.domain.errors import StorageError, NotFoundError

T = TypeVar('T')


class JsonStorageBase(Generic[T]):
    """Base class for JSON file storage."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _read_json(self, file_path: Path) -> Result[dict[str, Any], StorageError]:
        """Read JSON file."""
        try:
            if not file_path.exists():
                return Err(StorageError(
                    message=f"File not found: {file_path}",
                    operation="read",
                ))
            with open(file_path, 'r', encoding='utf-8') as f:
                return Ok(json.load(f))
        except json.JSONDecodeError as e:
            return Err(StorageError(
                message=f"Invalid JSON: {e}",
                operation="read",
            ))
        except OSError as e:
            return Err(StorageError(
                message=f"IO error: {e}",
                operation="read",
            ))

    def _write_json(self, file_path: Path, data: dict[str, Any]) -> Result[None, StorageError]:
        """Write JSON file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return Ok(None)
        except OSError as e:
            return Err(StorageError(
                message=f"IO error: {e}",
                operation="write",
            ))

    def _delete_file(self, file_path: Path) -> Result[None, NotFoundError]:
        """Delete file."""
        try:
            if not file_path.exists():
                return Err(NotFoundError(
                    entity="file",
                    id=str(file_path),
                ))
            file_path.unlink()
            return Ok(None)
        except OSError:
            return Err(NotFoundError(
                entity="file",
                id=str(file_path),
            ))
