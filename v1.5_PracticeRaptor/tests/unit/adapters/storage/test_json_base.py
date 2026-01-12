"""Tests for JsonStorageBase."""
import json
import pytest
from pathlib import Path
from typing import Any

from adapters.storage.json_base import JsonStorageBase


class ConcreteJsonStorage(JsonStorageBase[dict[str, Any]]):
    """Concrete implementation for testing."""
    pass


class TestJsonStorageBase:
    """Tests for JsonStorageBase."""

    def test_init_creates_directory(self, tmp_path: Path) -> None:
        """Test that __init__ creates the base directory."""
        base_path = tmp_path / "new_dir"
        assert not base_path.exists()

        ConcreteJsonStorage(base_path)

        assert base_path.exists()
        assert base_path.is_dir()

    def test_read_json_returns_data(self, tmp_path: Path) -> None:
        """Test reading a valid JSON file."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        file_path.write_text(json.dumps(data))

        result = storage._read_json(file_path)

        assert result.is_ok()
        assert result.unwrap() == data

    def test_read_json_returns_error_for_missing_file(self, tmp_path: Path) -> None:
        """Test that reading a missing file returns an error."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "nonexistent.json"

        result = storage._read_json(file_path)

        assert result.is_err()
        assert "not found" in result.error.message.lower()

    def test_read_json_returns_error_for_invalid_json(self, tmp_path: Path) -> None:
        """Test that reading invalid JSON returns an error."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json {")

        result = storage._read_json(file_path)

        assert result.is_err()
        assert "invalid json" in result.error.message.lower()

    def test_write_json_creates_file(self, tmp_path: Path) -> None:
        """Test writing a JSON file."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "output.json"
        data = {"key": "value"}

        result = storage._write_json(file_path, data)

        assert result.is_ok()
        assert file_path.exists()
        written = json.loads(file_path.read_text())
        assert written == data

    def test_write_json_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that write_json creates parent directories."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "nested" / "dir" / "output.json"
        data = {"key": "value"}

        result = storage._write_json(file_path, data)

        assert result.is_ok()
        assert file_path.exists()

    def test_delete_file_removes_existing_file(self, tmp_path: Path) -> None:
        """Test deleting an existing file."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "to_delete.json"
        file_path.write_text("{}")

        result = storage._delete_file(file_path)

        assert result.is_ok()
        assert not file_path.exists()

    def test_delete_file_returns_error_for_missing_file(self, tmp_path: Path) -> None:
        """Test that deleting a missing file returns an error."""
        storage = ConcreteJsonStorage(tmp_path)
        file_path = tmp_path / "nonexistent.json"

        result = storage._delete_file(file_path)

        assert result.is_err()
