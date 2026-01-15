"""Problem-related use cases.

Pure functions that orchestrate business logic.
Each function receives dependencies as parameters (DI).
"""

import random
from dataclasses import dataclass

from core.models.domain.enums import Category, Difficulty, ProblemStatus
from core.models.domain.problem import Problem, ProblemSummary
from core.ports.repositories import IProblemRepository


# ============================================================
# Use Cases
# ============================================================


def get_problem(
    problem_id: int,
    repo: IProblemRepository,
) -> Problem | None:
    """Get complete problem by ID.

    Use when user selects a specific problem to solve.

    Args:
        problem_id: Problem ID
        repo: Problem repository (any implementation)

    Returns:
        Problem with all details or None if not found

    Example:
        problem = get_problem(1, json_repo)
        if problem:
            print(problem.title.get("ru"))
    """
    return repo.get_by_id(problem_id)


def get_problem_summaries(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    category: Category | None = None,
    tag: str | None = None,
    status: ProblemStatus | None = None,
) -> list[ProblemSummary]:
    """Get filtered problem list for display.

    Use for problem list view with filters.

    Args:
        repo: Problem repository
        difficulty: Filter by difficulty (optional)
        category: Filter by category (optional)
        tag: Filter by tag (optional)
        status: Filter by user's progress status (optional)

    Returns:
        List of lightweight ProblemSummary objects

    Example:
        # Get all easy problems
        problems = get_problem_summaries(repo, difficulty=Difficulty.EASY)

        # Get problems with specific tag
        problems = get_problem_summaries(repo, tag="hash-table")
    """
    summaries = repo.get_all_summaries(
        difficulty=difficulty,
        category=category,
        tag=tag,
    )

    # Filter by status if specified (done in memory, since status comes from user progress)
    if status is not None:
        summaries = [s for s in summaries if s.status == status]

    return summaries


def get_random_problem(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    category: Category | None = None,
    exclude_ids: list[int] | None = None,
) -> Problem | None:
    """Get random problem matching criteria.

    Use for "random problem" feature.

    Args:
        repo: Problem repository
        difficulty: Filter by difficulty (optional)
        category: Filter by category (optional)
        exclude_ids: Problem IDs to exclude (e.g., already solved)

    Returns:
        Random Problem or None if no matching problems

    Example:
        # Random easy problem, excluding already solved
        problem = get_random_problem(
            repo,
            difficulty=Difficulty.EASY,
            exclude_ids=[1, 2, 3],
        )
    """
    summaries = get_problem_summaries(
        repo=repo,
        difficulty=difficulty,
        category=category,
    )

    # Exclude specified IDs
    exclude_set = set(exclude_ids or [])
    available = [s for s in summaries if s.id not in exclude_set]

    if not available:
        return None

    chosen = random.choice(available)
    return repo.get_by_id(chosen.id)


# ============================================================
# Display Helpers
# ============================================================


@dataclass
class ProblemDisplayData:
    """Formatted problem data for UI display."""

    id: int
    title: str
    description: str
    difficulty: str
    difficulty_label: str
    categories: list[str]
    tags: list[str]
    examples: list[dict]
    hints: list[str]
    editorial: str | None


def format_problem_for_display(
    problem: Problem,
    locale: str = "en",
    show_editorial: bool = False,
) -> ProblemDisplayData:
    """Format problem for UI display.

    Extracts all localized content and formats for rendering.

    Args:
        problem: Problem domain model
        locale: Language for content
        show_editorial: Include editorial (only after solving)

    Returns:
        ProblemDisplayData with all strings ready for display

    Example:
        data = format_problem_for_display(problem, locale="ru")
        print(data.title)        # "Два числа"
        print(data.difficulty)   # "easy"
        print(data.examples[0])  # {"input": "...", "output": "...", "explanation": "..."}
    """
    # Format difficulty label
    difficulty_labels = {
        "easy": {"en": "Easy", "ru": "Лёгкая"},
        "medium": {"en": "Medium", "ru": "Средняя"},
        "hard": {"en": "Hard", "ru": "Сложная"},
    }
    diff_value = problem.difficulty.value
    difficulty_label = difficulty_labels.get(diff_value, {}).get(locale, diff_value)

    # Format examples
    examples = []
    for i, example in enumerate(problem.examples, 1):
        ex_data = {
            "number": i,
            "input": example.input,
            "output": example.output,
        }
        explanation = example.explanation.get(locale)
        if explanation:
            ex_data["explanation"] = explanation
        examples.append(ex_data)

    # Format hints
    hints = [hint.get(locale) for hint in problem.hints if hint.get(locale)]

    # Editorial (only if requested)
    editorial = None
    if show_editorial:
        editorial = problem.editorial.get(locale) or None

    return ProblemDisplayData(
        id=problem.id,
        title=problem.title.get(locale),
        description=problem.description.get(locale),
        difficulty=diff_value,
        difficulty_label=difficulty_label,
        categories=[c.value for c in problem.categories],
        tags=list(problem.tags),
        examples=examples,
        hints=hints,
        editorial=editorial,
    )
