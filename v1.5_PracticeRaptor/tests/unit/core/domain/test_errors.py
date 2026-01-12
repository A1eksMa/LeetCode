"""Tests for domain errors."""
import pytest
from core.domain.errors import (
    DomainError,
    NotFoundError,
    ValidationError,
    ExecutionError,
    StorageError,
)


class TestDomainError:
    def test_message_accessible(self) -> None:
        error = DomainError(message="Something went wrong")
        assert error.message == "Something went wrong"

    def test_str_returns_message(self) -> None:
        error = DomainError(message="Something went wrong")
        assert str(error) == "Something went wrong"


class TestNotFoundError:
    def test_message_auto_generated(self) -> None:
        error = NotFoundError(entity="User", id="123")
        assert error.message == "User with id '123' not found"

    def test_entity_and_id_accessible(self) -> None:
        error = NotFoundError(entity="Problem", id=42)
        assert error.entity == "Problem"
        assert error.id == 42


class TestValidationError:
    def test_with_field(self) -> None:
        error = ValidationError(message="Invalid value", field="email")
        assert error.message == "Invalid value"
        assert error.field == "email"

    def test_without_field(self) -> None:
        error = ValidationError(message="Invalid data")
        assert error.field is None


class TestExecutionError:
    def test_with_error_type(self) -> None:
        error = ExecutionError(message="Code timed out", error_type="timeout")
        assert error.message == "Code timed out"
        assert error.error_type == "timeout"


class TestStorageError:
    def test_with_operation(self) -> None:
        error = StorageError(message="Cannot write file", operation="write")
        assert error.message == "Cannot write file"
        assert error.operation == "write"


class TestErrorImmutability:
    def test_domain_error_is_frozen(self) -> None:
        error = DomainError(message="test")
        with pytest.raises(AttributeError):
            error.message = "new message"  # type: ignore

    def test_not_found_error_is_frozen(self) -> None:
        error = NotFoundError(entity="User", id="123")
        with pytest.raises(AttributeError):
            error.entity = "Other"  # type: ignore
