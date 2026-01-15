"""Repository interfaces (Ports)."""

from typing import Protocol

from core.models.domain.problem import Problem, ProblemSummary
from core.models.domain.enums import Difficulty, Category, ProblemStatus


class IProblemRepository(Protocol):
    """Interface for problem storage.

    Implementations: JsonProblemRepository, SqliteProblemRepository
    """

    def get_by_id(self, problem_id: int) -> Problem | None:
        """Get complete problem by ID.

        Args:
            problem_id: Problem ID

        Returns:
            Problem with all details or None if not found
        """
        ...

    def get_all_summaries(
        self,
        difficulty: Difficulty | None = None,
        category: Category | None = None,
        tag: str | None = None,
    ) -> list[ProblemSummary]:
        """Get lightweight problem list for display.

        Args:
            difficulty: Filter by difficulty
            category: Filter by category
            tag: Filter by tag

        Returns:
            List of ProblemSummary for list view
        """
        ...

    def get_problem_ids(self) -> list[int]:
        """Get all problem IDs."""
        ...

    def count(self) -> int:
        """Get total number of problems."""
        ...
