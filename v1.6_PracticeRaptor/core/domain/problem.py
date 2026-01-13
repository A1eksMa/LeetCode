"""Problem-related domain models."""

from dataclasses import dataclass

from .enums import (
    Category,
    Complexity,
    Difficulty,
    Language,
    ProgrammingLanguage,
    ProblemStatus,
)


@dataclass(frozen=True)
class Problem:
    """Minimal problem entity for list display.

    Lightweight model loaded for all problems in list view.
    Title is fetched separately from localization (Title entity).
    """

    problem_id: int = 0
    status: ProblemStatus = ProblemStatus.NOT_STARTED


@dataclass(frozen=True)
class ProblemSelector:
    """Problem metadata for filtering and selection.

    Contains all data needed for filtering problems without
    loading heavy content like descriptions.
    """

    problem_id: int = 0
    supported_languages: tuple[Language, ...] = ()
    supported_programming_languages: tuple[ProgrammingLanguage, ...] = ()
    difficulty: Difficulty = Difficulty.EASY
    tags: tuple[str, ...] = ()
    categories: tuple[Category, ...] = ()


@dataclass(frozen=True)
class Example:
    """Problem example with input/output.

    Explanation is stored separately in Explanation entity (localized).
    """

    example_id: int
    problem_id: int
    input: str = ""
    output: str = ""


@dataclass(frozen=True)
class ProblemDescription:
    """Complete problem description with all details.

    Heavyweight model loaded only when user selects a specific problem.
    Textual content (description, editorial, hints) is stored
    in separate localized entities.
    """

    problem_id: int = 0
    complexity: Complexity = Complexity.O_N
    examples: tuple[Example, ...] = ()
