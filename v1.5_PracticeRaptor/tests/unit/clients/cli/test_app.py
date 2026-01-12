"""Tests for CLI application."""
import pytest
from unittest.mock import MagicMock, patch

from clients.cli.app import CLIApp
from core.domain.models import Problem, LocalizedText, LanguageSpec, ExecutionResult
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok, Err
from core.domain.errors import ExecutionError


@pytest.fixture
def cli_app(mock_container):
    """Create CLIApp with mock container."""
    return CLIApp(mock_container)


@pytest.fixture
def sample_problems():
    """Create sample problems tuple."""
    return (
        Problem(
            id=1,
            title=LocalizedText({"en": "Two Sum"}),
            description=LocalizedText({"en": "Find two numbers..."}),
            difficulty=Difficulty.EASY,
            tags=("array",),
            examples=(),
            test_cases=(),
            languages=(
                LanguageSpec(
                    language=Language.PYTHON,
                    function_signature="def two_sum(nums, target):",
                    solutions=(),
                ),
            ),
        ),
        Problem(
            id=2,
            title=LocalizedText({"en": "Reverse String"}),
            description=LocalizedText({"en": "Reverse a string..."}),
            difficulty=Difficulty.EASY,
            tags=("string",),
            examples=(),
            test_cases=(),
            languages=(
                LanguageSpec(
                    language=Language.PYTHON,
                    function_signature="def reverse_string(s):",
                    solutions=(),
                ),
            ),
        ),
    )


class TestCLIApp:
    """Tests for CLIApp class."""

    def test_init_sets_locale_from_container(self, mock_container):
        """App should use locale from container."""
        mock_container.default_locale = "ru"
        app = CLIApp(mock_container)
        assert app.locale == "ru"

    def test_init_sets_default_language(self, cli_app):
        """App should default to Python language."""
        assert cli_app.language == Language.PYTHON

    def test_run_returns_1_when_no_problems(self, cli_app):
        """Run should return 1 when no problems found."""
        with patch("clients.cli.app.get_all_problems", return_value=()):
            with patch("clients.cli.app.display_message"):
                result = cli_app.run()

        assert result == 1

    def test_run_displays_welcome(self, cli_app, sample_problems):
        """Run should display welcome banner."""
        with patch("clients.cli.app.get_all_problems", return_value=sample_problems):
            with patch("clients.cli.app.display_welcome") as mock_welcome:
                with patch.object(CLIApp, "_run_interactive", return_value=0):
                    cli_app.run()

        mock_welcome.assert_called_once()

    def test_run_file_mode_returns_1_when_file_not_found(self, cli_app, sample_problems):
        """File mode should return 1 when file not found."""
        with patch("clients.cli.app.get_all_problems", return_value=sample_problems):
            with patch("clients.cli.app.display_welcome"):
                with patch(
                    "clients.cli.app.read_code_from_file",
                    side_effect=FileNotFoundError,
                ):
                    with patch("clients.cli.app.display_message"):
                        result = cli_app.run(file_path="nonexistent.py")

        assert result == 1

    def test_run_single_task_returns_1_when_task_not_found(
        self, cli_app, sample_problems
    ):
        """Single task mode should return 1 for invalid task ID."""
        with patch("clients.cli.app.get_all_problems", return_value=sample_problems):
            with patch("clients.cli.app.display_welcome"):
                with patch("clients.cli.app.display_message"):
                    result = cli_app.run(task_id=999)

        assert result == 1

    def test_get_problem_by_index_returns_problem(self, cli_app, sample_problems):
        """Should return problem for valid index."""
        problem = cli_app._get_problem_by_index(sample_problems, 1)
        assert problem is not None
        assert problem.id == 1

    def test_get_problem_by_index_returns_none_for_invalid_index(
        self, cli_app, sample_problems
    ):
        """Should return None for invalid index."""
        assert cli_app._get_problem_by_index(sample_problems, 0) is None
        assert cli_app._get_problem_by_index(sample_problems, 10) is None

    def test_run_interactive_exits_on_keyboard_interrupt(
        self, cli_app, sample_problems
    ):
        """Interactive mode should exit gracefully on Ctrl+C."""
        with patch("clients.cli.app.get_all_problems", return_value=sample_problems):
            with patch("clients.cli.app.display_welcome"):
                with patch.object(
                    CLIApp, "_select_problem", side_effect=KeyboardInterrupt
                ):
                    with patch("clients.cli.app.display_message"):
                        result = cli_app.run()

        assert result == 0


class TestCLIAppSolving:
    """Tests for problem solving flow."""

    def test_run_and_display_results_success(self, cli_app, sample_problems):
        """Should return True when tests pass."""
        exec_result = ExecutionResult(
            success=True,
            test_results=(),
            total_time_ms=10,
        )

        cli_app.container.executor = MagicMock()

        with patch("clients.cli.app.run_full_tests", return_value=Ok(exec_result)):
            with patch("clients.cli.app.display_results"):
                result = cli_app._run_and_display_results(
                    sample_problems[0], "def two_sum(): pass", False
                )

        assert result is True

    def test_run_and_display_results_failure(self, cli_app, sample_problems):
        """Should return False when tests fail."""
        exec_result = ExecutionResult(
            success=False,
            test_results=(),
            total_time_ms=10,
        )

        with patch("clients.cli.app.run_full_tests", return_value=Ok(exec_result)):
            with patch("clients.cli.app.display_results"):
                result = cli_app._run_and_display_results(
                    sample_problems[0], "def two_sum(): pass", False
                )

        assert result is False

    def test_run_and_display_results_error(self, cli_app, sample_problems):
        """Should return False on execution error."""
        error = ExecutionError(message="Execution failed", error_type="runtime")

        with patch("clients.cli.app.run_full_tests", return_value=Err(error)):
            with patch("clients.cli.app.display_message"):
                result = cli_app._run_and_display_results(
                    sample_problems[0], "def two_sum(): pass", False
                )

        assert result is False
