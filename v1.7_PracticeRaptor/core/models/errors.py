"""Domain error types."""

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class DomainError:
    """Base class for domain errors."""

    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class NotFoundError(DomainError):
    """Entity not found."""

    entity: str = ""
    id: Union[str, int] = ""
    message: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            'message',
            f"{self.entity} with id '{self.id}' not found"
        )


@dataclass(frozen=True)
class ValidationError(DomainError):
    """Validation failed."""

    field: Union[str, None] = None


@dataclass(frozen=True)
class ExecutionError(DomainError):
    """Code execution failed."""

    error_type: str = ""  # syntax, runtime, timeout, memory


@dataclass(frozen=True)
class StorageError(DomainError):
    """Storage operation failed."""

    operation: str = ""  # read, write, delete
