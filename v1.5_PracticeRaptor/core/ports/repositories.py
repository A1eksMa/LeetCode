"""Repository interfaces (Ports)."""
from typing import Protocol

from core.domain.models import (
    Problem,
    User,
    Draft,
    Submission,
    Progress,
)
from core.domain.enums import Difficulty, Language
from core.domain.result import Result
from core.domain.errors import NotFoundError, StorageError


class IProblemRepository(Protocol):
    """Interface for problem storage."""

    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
        """Get problem by ID."""
        ...

    def get_all(self) -> tuple[Problem, ...]:
        """Get all problems."""
        ...

    def filter(
        self,
        difficulty: Difficulty | None = None,
        tags: tuple[str, ...] | None = None,
        language: Language | None = None,
    ) -> tuple[Problem, ...]:
        """Filter problems by criteria."""
        ...

    def count(self) -> int:
        """Get total number of problems."""
        ...


class IUserRepository(Protocol):
    """Interface for user storage."""

    def get_by_id(self, user_id: str) -> Result[User, NotFoundError]:
        """Get user by ID."""
        ...

    def save(self, user: User) -> Result[User, StorageError]:
        """Save user (create or update)."""
        ...

    def delete(self, user_id: str) -> Result[None, NotFoundError]:
        """Delete user."""
        ...


class IDraftRepository(Protocol):
    """Interface for draft storage."""

    def get(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[Draft, NotFoundError]:
        """Get draft for user/problem/language combination."""
        ...

    def save(self, draft: Draft) -> Result[Draft, StorageError]:
        """Save draft (overwrites existing)."""
        ...

    def delete(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[None, NotFoundError]:
        """Delete draft."""
        ...

    def get_all_for_user(self, user_id: str) -> tuple[Draft, ...]:
        """Get all drafts for a user."""
        ...


class ISubmissionRepository(Protocol):
    """Interface for submission storage."""

    def get_by_id(self, submission_id: str) -> Result[Submission, NotFoundError]:
        """Get submission by ID."""
        ...

    def save(self, submission: Submission) -> Result[Submission, StorageError]:
        """Save new submission."""
        ...

    def get_for_problem(
        self,
        user_id: str,
        problem_id: int,
    ) -> tuple[Submission, ...]:
        """Get all submissions for user/problem."""
        ...

    def get_for_user(self, user_id: str) -> tuple[Submission, ...]:
        """Get all submissions for user."""
        ...


class IProgressRepository(Protocol):
    """Interface for progress storage."""

    def get(
        self,
        user_id: str,
        problem_id: int,
    ) -> Result[Progress, NotFoundError]:
        """Get progress for user/problem."""
        ...

    def save(self, progress: Progress) -> Result[Progress, StorageError]:
        """Save progress."""
        ...

    def get_all_for_user(self, user_id: str) -> tuple[Progress, ...]:
        """Get all progress entries for user."""
        ...

    def get_solved_count(self, user_id: str) -> int:
        """Get number of solved problems for user."""
        ...

    def get_solved_by_difficulty(
        self,
        user_id: str,
    ) -> dict[Difficulty, int]:
        """Get solved count grouped by difficulty."""
        ...
