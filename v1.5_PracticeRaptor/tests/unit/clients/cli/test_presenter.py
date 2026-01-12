"""Tests for CLI presenter."""
import pytest
from io import StringIO
from unittest.mock import patch

from clients.cli.presenter import (
    display_welcome,
    display_problem_list,
    display_problem,
    display_results,
    display_hint,
    display_message,
    _get_difficulty_color,
    _format_input,
)
from clients.cli.colors import Colors
from core.domain.models import (
    Problem,
    LocalizedText,
    LanguageSpec,
    Solution,
    ExecutionResult,
    TestResult,
    TestCase,
)
from core.domain.enums import Difficulty, Language


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id=1,
        title=LocalizedText({"en": "Two Sum", "ru": "Сумма"}),
        description=LocalizedText({"en": "Find two numbers that add up to target."}),
        difficulty=Difficulty.EASY,
        tags=("array", "hash-table"),
        examples=(),
        test_cases=(),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def two_sum(nums, target):",
                solutions=(
                    Solution(
                        name="Hash Map",
                        complexity="O(n)",
                        code="def two_sum(nums, target): pass",
                    ),
                ),
            ),
        ),
    )


class TestDisplayWelcome:
    """Tests for display_welcome function."""

    def test_displays_banner(self, capsys):
        """Should display PracticeRaptor banner."""
        display_welcome()
        captured = capsys.readouterr()
        assert "PracticeRaptor" in captured.out


class TestDisplayProblemList:
    """Tests for display_problem_list function."""

    def test_displays_random_option(self, capsys, sample_problem):
        """Should display random problem option."""
        display_problem_list((sample_problem,), "en")
        captured = capsys.readouterr()
        assert "Random problem" in captured.out
        # ANSI codes may be present around the number
        assert "0" in captured.out

    def test_displays_problems(self, capsys, sample_problem):
        """Should display problem titles."""
        display_problem_list((sample_problem,), "en")
        captured = capsys.readouterr()
        assert "Two Sum" in captured.out
        assert "[1]" in captured.out

    def test_displays_difficulty(self, capsys, sample_problem):
        """Should display difficulty."""
        display_problem_list((sample_problem,), "en")
        captured = capsys.readouterr()
        assert "easy" in captured.out

    def test_displays_tags(self, capsys, sample_problem):
        """Should display tags."""
        display_problem_list((sample_problem,), "en")
        captured = capsys.readouterr()
        assert "array" in captured.out
        assert "hash-table" in captured.out


class TestDisplayProblem:
    """Tests for display_problem function."""

    def test_displays_title(self, capsys, sample_problem):
        """Should display problem title."""
        display_problem(sample_problem, Language.PYTHON, "en")
        captured = capsys.readouterr()
        assert "Two Sum" in captured.out

    def test_displays_description(self, capsys, sample_problem):
        """Should display problem description."""
        display_problem(sample_problem, Language.PYTHON, "en")
        captured = capsys.readouterr()
        assert "Find two numbers" in captured.out

    def test_displays_function_signature(self, capsys, sample_problem):
        """Should display function signature."""
        display_problem(sample_problem, Language.PYTHON, "en")
        captured = capsys.readouterr()
        assert "def two_sum" in captured.out


class TestDisplayResults:
    """Tests for display_results function."""

    def test_displays_success(self, capsys):
        """Should display success message."""
        result = ExecutionResult(
            success=True,
            test_results=(),
            total_time_ms=10,
        )
        display_results(result)
        captured = capsys.readouterr()
        assert "All tests passed" in captured.out

    def test_displays_failure(self, capsys):
        """Should display failure message."""
        result = ExecutionResult(
            success=False,
            test_results=(
                TestResult(
                    test_case=TestCase(
                        input={"x": 1},
                        expected=2,
                    ),
                    passed=False,
                    actual=0,
                    error_message="Expected 2, got 0",
                ),
            ),
            total_time_ms=10,
        )
        display_results(result)
        captured = capsys.readouterr()
        assert "Tests failed" in captured.out

    def test_displays_execution_time(self, capsys):
        """Should display execution time."""
        result = ExecutionResult(
            success=True,
            test_results=(),
            total_time_ms=42,
        )
        display_results(result)
        captured = capsys.readouterr()
        assert "42ms" in captured.out


class TestDisplayHint:
    """Tests for display_hint function."""

    def test_displays_solution_name(self, capsys):
        """Should display solution name."""
        display_hint("Hash Map", "O(n)", "def solution(): pass", 1, 2)
        captured = capsys.readouterr()
        assert "Hash Map" in captured.out

    def test_displays_complexity(self, capsys):
        """Should display complexity."""
        display_hint("Hash Map", "O(n)", "def solution(): pass", 1, 2)
        captured = capsys.readouterr()
        assert "O(n)" in captured.out

    def test_displays_hint_number(self, capsys):
        """Should display hint number."""
        display_hint("Hash Map", "O(n)", "def solution(): pass", 1, 2)
        captured = capsys.readouterr()
        assert "1/2" in captured.out


class TestDisplayMessage:
    """Tests for display_message function."""

    def test_displays_info_message(self, capsys):
        """Should display info message."""
        display_message("Test info", "info")
        captured = capsys.readouterr()
        assert "Test info" in captured.out

    def test_displays_error_message(self, capsys):
        """Should display error message."""
        display_message("Test error", "error")
        captured = capsys.readouterr()
        assert "Test error" in captured.out


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_difficulty_color_easy(self):
        """Easy difficulty should be green."""
        color = _get_difficulty_color(Difficulty.EASY)
        assert color == Colors.GREEN

    def test_get_difficulty_color_medium(self):
        """Medium difficulty should be yellow."""
        color = _get_difficulty_color(Difficulty.MEDIUM)
        assert color == Colors.YELLOW

    def test_get_difficulty_color_hard(self):
        """Hard difficulty should be red."""
        color = _get_difficulty_color(Difficulty.HARD)
        assert color == Colors.RED

    def test_format_input_single_value(self):
        """Should format single input value."""
        result = _format_input({"x": 5})
        assert result == "x = 5"

    def test_format_input_multiple_values(self):
        """Should format multiple input values."""
        result = _format_input({"nums": [1, 2], "target": 3})
        assert "nums = [1, 2]" in result
        assert "target = 3" in result
