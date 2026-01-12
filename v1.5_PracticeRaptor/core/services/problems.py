"""Problem-related pure functions."""
import random

from core.domain.models import Problem
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError
from core.ports.repositories import IProblemRepository


def get_problem(
    problem_id: int,
    repo: IProblemRepository,
) -> Result[Problem, NotFoundError]:
    """Get problem by ID."""
    return repo.get_by_id(problem_id)


def get_all_problems(repo: IProblemRepository) -> tuple[Problem, ...]:
    """Get all problems sorted by ID."""
    return repo.get_all()


def filter_problems(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    tags: tuple[str, ...] | None = None,
    language: Language | None = None,
) -> tuple[Problem, ...]:
    """Filter problems by criteria."""
    return repo.filter(difficulty=difficulty, tags=tags, language=language)


def get_random_problem(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    tags: tuple[str, ...] | None = None,
    language: Language | None = None,
    exclude_ids: tuple[int, ...] = (),
) -> Result[Problem, NotFoundError]:
    """Get random problem matching criteria."""
    problems = filter_problems(repo, difficulty, tags, language)
    available = tuple(p for p in problems if p.id not in exclude_ids)

    if not available:
        return Err(NotFoundError(
            entity="Problem",
            id="random",
        ))

    return Ok(random.choice(available))


def get_problem_display_text(
    problem: Problem,
    locale: str = "en",
) -> dict[str, str]:
    """Get problem text for display."""
    return {
        "title": problem.title.get(locale),
        "description": problem.description.get(locale),
        "difficulty": problem.difficulty.value,
        "tags": ", ".join(problem.tags),
    }


def format_examples(
    problem: Problem,
    locale: str = "en",
) -> list[dict]:
    """Format examples for display."""
    result = []
    for i, example in enumerate(problem.examples, 1):
        item = {
            "number": i,
            "input": example.input,
            "output": example.output,
        }
        if example.explanation:
            item["explanation"] = example.explanation.get(locale)
        result.append(item)
    return result
