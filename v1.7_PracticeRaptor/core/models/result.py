"""Result type for functional error handling."""

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Union

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Success case of Result."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def map(self, fn: Callable[[T], U]) -> 'Ok[U]':
        """Apply function to value if Ok."""
        return Ok(fn(self.value))

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Apply function that returns Result."""
        return fn(self.value)

    def unwrap(self) -> T:
        """Get value or raise if Err."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get value or default."""
        return self.value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True)
class Err(Generic[E]):
    """Error case of Result."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def map(self, fn: Callable[[T], U]) -> 'Err[E]':
        """Return self (error propagates)."""
        return self

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Err[E]':
        """Return self (error propagates)."""
        return self

    def unwrap(self) -> None:
        """Raise ValueError with error details."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Return default value."""
        return default

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# Type alias
Result = Union[Ok[T], Err[E]]
