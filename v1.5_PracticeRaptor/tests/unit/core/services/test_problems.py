"""Tests for problems service functions."""
import pytest
from typing import Any
from unittest.mock import Mock

from core.domain.models import Problem, LocalizedText, Example
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok, Err
from core.domain.errors import NotFoundError
from core.services.problems import (
    get_problem,
    get_all_problems,
    filter_problems,
    get_random_problem,
    get_problem_display_text,
    format_examples,
)


def make_problem(
    id: int,
    title: str = "Test Problem",
    difficulty: Difficulty = Difficulty.EASY,
    tags: tuple[str, ...] = (),
    examples: tuple[Example, ...] = (),
) -> Problem:
    """Create a test problem."""
    return Problem(
        id=id,
        title=LocalizedText({"en": title, "ru": f"{title} (RU)"}),
        description=LocalizedText({"en": f"Description for {title}"}),
        difficulty=difficulty,
        tags=tags,
        examples=examples,
    )


class TestGetProblem:
    """Tests for get_problem function."""

    def test_returns_problem_when_found(self) -> None:
        """Return problem when repository finds it."""
        problem = make_problem(1, "Two Sum")
        repo = Mock()
        repo.get_by_id.return_value = Ok(problem)

        result = get_problem(1, repo)

        assert result.is_ok()
        assert result.unwrap() == problem
        repo.get_by_id.assert_called_once_with(1)

    def test_returns_error_when_not_found(self) -> None:
        """Return error when problem not found."""
        repo = Mock()
        repo.get_by_id.return_value = Err(NotFoundError(entity="Problem", id=999))

        result = get_problem(999, repo)

        assert result.is_err()
        assert isinstance(result.error, NotFoundError)


class TestGetAllProblems:
    """Tests for get_all_problems function."""

    def test_returns_all_problems(self) -> None:
        """Return all problems from repository."""
        problems = (
            make_problem(1, "Problem 1"),
            make_problem(2, "Problem 2"),
            make_problem(3, "Problem 3"),
        )
        repo = Mock()
        repo.get_all.return_value = problems

        result = get_all_problems(repo)

        assert result == problems
        repo.get_all.assert_called_once()

    def test_returns_empty_tuple_when_no_problems(self) -> None:
        """Return empty tuple when no problems exist."""
        repo = Mock()
        repo.get_all.return_value = ()

        result = get_all_problems(repo)

        assert result == ()


class TestFilterProblems:
    """Tests for filter_problems function."""

    def test_filters_by_difficulty(self) -> None:
        """Filter problems by difficulty."""
        repo = Mock()
        repo.filter.return_value = (make_problem(1),)

        result = filter_problems(repo, difficulty=Difficulty.EASY)

        repo.filter.assert_called_once_with(
            difficulty=Difficulty.EASY,
            tags=None,
            language=None,
        )

    def test_filters_by_tags(self) -> None:
        """Filter problems by tags."""
        repo = Mock()
        repo.filter.return_value = ()

        filter_problems(repo, tags=("array", "hash"))

        repo.filter.assert_called_once_with(
            difficulty=None,
            tags=("array", "hash"),
            language=None,
        )

    def test_filters_by_language(self) -> None:
        """Filter problems by language."""
        repo = Mock()
        repo.filter.return_value = ()

        filter_problems(repo, language=Language.PYTHON)

        repo.filter.assert_called_once_with(
            difficulty=None,
            tags=None,
            language=Language.PYTHON,
        )

    def test_filters_by_multiple_criteria(self) -> None:
        """Filter problems by multiple criteria."""
        repo = Mock()
        repo.filter.return_value = ()

        filter_problems(
            repo,
            difficulty=Difficulty.MEDIUM,
            tags=("dp",),
            language=Language.PYTHON,
        )

        repo.filter.assert_called_once_with(
            difficulty=Difficulty.MEDIUM,
            tags=("dp",),
            language=Language.PYTHON,
        )


class TestGetRandomProblem:
    """Tests for get_random_problem function."""

    def test_returns_random_problem(self) -> None:
        """Return a random problem from filtered results."""
        problems = (
            make_problem(1, "Problem 1"),
            make_problem(2, "Problem 2"),
        )
        repo = Mock()
        repo.filter.return_value = problems

        result = get_random_problem(repo)

        assert result.is_ok()
        assert result.unwrap() in problems

    def test_excludes_specified_ids(self) -> None:
        """Exclude problems with specified IDs."""
        problems = (
            make_problem(1, "Problem 1"),
            make_problem(2, "Problem 2"),
            make_problem(3, "Problem 3"),
        )
        repo = Mock()
        repo.filter.return_value = problems

        result = get_random_problem(repo, exclude_ids=(1, 2))

        assert result.is_ok()
        assert result.unwrap().id == 3

    def test_returns_error_when_no_matching_problems(self) -> None:
        """Return error when no problems match criteria."""
        repo = Mock()
        repo.filter.return_value = ()

        result = get_random_problem(repo)

        assert result.is_err()
        assert isinstance(result.error, NotFoundError)

    def test_returns_error_when_all_excluded(self) -> None:
        """Return error when all matching problems are excluded."""
        problems = (make_problem(1), make_problem(2))
        repo = Mock()
        repo.filter.return_value = problems

        result = get_random_problem(repo, exclude_ids=(1, 2))

        assert result.is_err()


class TestGetProblemDisplayText:
    """Tests for get_problem_display_text function."""

    def test_returns_english_text_by_default(self) -> None:
        """Return English text by default."""
        problem = make_problem(
            1,
            title="Two Sum",
            difficulty=Difficulty.EASY,
            tags=("array", "hash"),
        )

        result = get_problem_display_text(problem)

        assert result["title"] == "Two Sum"
        assert result["difficulty"] == "easy"
        assert result["tags"] == "array, hash"

    def test_returns_localized_text(self) -> None:
        """Return text in specified locale."""
        problem = make_problem(1, title="Two Sum")

        result = get_problem_display_text(problem, locale="ru")

        assert result["title"] == "Two Sum (RU)"

    def test_falls_back_to_english(self) -> None:
        """Fall back to English if locale not available."""
        problem = make_problem(1, title="Two Sum")

        result = get_problem_display_text(problem, locale="de")

        assert result["title"] == "Two Sum"


class TestFormatExamples:
    """Tests for format_examples function."""

    def test_formats_examples_with_numbers(self) -> None:
        """Format examples with sequential numbers."""
        examples = (
            Example(
                input={"nums": [1, 2], "target": 3},
                output=[0, 1],
            ),
            Example(
                input={"nums": [2, 7], "target": 9},
                output=[0, 1],
            ),
        )
        problem = make_problem(1, examples=examples)

        result = format_examples(problem)

        assert len(result) == 2
        assert result[0]["number"] == 1
        assert result[1]["number"] == 2

    def test_includes_input_output(self) -> None:
        """Include input and output in formatted examples."""
        examples = (
            Example(
                input={"x": 5},
                output=25,
            ),
        )
        problem = make_problem(1, examples=examples)

        result = format_examples(problem)

        assert result[0]["input"] == {"x": 5}
        assert result[0]["output"] == 25

    def test_includes_explanation_if_present(self) -> None:
        """Include explanation if present."""
        examples = (
            Example(
                input={"x": 5},
                output=25,
                explanation=LocalizedText({"en": "5 squared is 25"}),
            ),
        )
        problem = make_problem(1, examples=examples)

        result = format_examples(problem)

        assert result[0]["explanation"] == "5 squared is 25"

    def test_omits_explanation_if_none(self) -> None:
        """Omit explanation key if not present."""
        examples = (
            Example(
                input={"x": 5},
                output=25,
            ),
        )
        problem = make_problem(1, examples=examples)

        result = format_examples(problem)

        assert "explanation" not in result[0]

    def test_returns_empty_list_for_no_examples(self) -> None:
        """Return empty list when no examples."""
        problem = make_problem(1)

        result = format_examples(problem)

        assert result == []
