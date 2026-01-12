"""Tests for CLI input handler."""
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import tempfile
from pathlib import Path

from clients.cli.input_handler import (
    InputResult,
    get_user_choice,
    read_user_code,
    read_code_from_file,
    ask_continue,
    ask_retry,
)
from core.domain.models import Problem, LocalizedText, LanguageSpec, Solution
from core.domain.enums import Difficulty, Language


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id=1,
        title=LocalizedText({"en": "Test Problem"}),
        description=LocalizedText({"en": "Test description"}),
        difficulty=Difficulty.EASY,
        tags=(),
        examples=(),
        test_cases=(),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def solution(x):",
                solutions=(
                    Solution(
                        name="Simple",
                        complexity="O(1)",
                        code="def solution(x): return x",
                    ),
                ),
            ),
        ),
    )


class TestInputResult:
    """Tests for InputResult dataclass."""

    def test_default_values(self):
        """Should have default values."""
        result = InputResult()
        assert result.code is None
        assert result.cancelled is False

    def test_with_code(self):
        """Should store code."""
        result = InputResult(code="def foo(): pass")
        assert result.code == "def foo(): pass"
        assert result.cancelled is False

    def test_cancelled(self):
        """Should store cancelled flag."""
        result = InputResult(cancelled=True)
        assert result.code is None
        assert result.cancelled is True


class TestGetUserChoice:
    """Tests for get_user_choice function."""

    def test_valid_choice(self):
        """Should return valid choice."""
        with patch("builtins.input", return_value="2"):
            result = get_user_choice(1, 5)
        assert result == 2

    def test_min_value(self):
        """Should accept min value."""
        with patch("builtins.input", return_value="0"):
            result = get_user_choice(0, 5)
        assert result == 0

    def test_max_value(self):
        """Should accept max value."""
        with patch("builtins.input", return_value="5"):
            result = get_user_choice(1, 5)
        assert result == 5

    def test_retries_on_invalid_input(self, capsys):
        """Should retry on invalid input."""
        with patch("builtins.input", side_effect=["abc", "2"]):
            result = get_user_choice(1, 5)
        assert result == 2
        captured = capsys.readouterr()
        assert "Enter a number" in captured.out

    def test_retries_on_out_of_range(self, capsys):
        """Should retry on out of range input."""
        with patch("builtins.input", side_effect=["10", "2"]):
            result = get_user_choice(1, 5)
        assert result == 2
        captured = capsys.readouterr()
        assert "from 1 to 5" in captured.out


class TestReadUserCode:
    """Tests for read_user_code function."""

    def test_reads_multiline_code(self, sample_problem):
        """Should read multiline code ending with double enter."""
        inputs = ["def foo():", "    return 1", "", ""]
        with patch("builtins.input", side_effect=inputs):
            result = read_user_code(sample_problem, Language.PYTHON)

        assert result.code is not None
        assert "def foo():" in result.code
        assert "return 1" in result.code
        assert result.cancelled is False

    def test_cancel_command(self, sample_problem):
        """!cancel should cancel input."""
        with patch("builtins.input", side_effect=["!cancel"]):
            result = read_user_code(sample_problem, Language.PYTHON)

        assert result.cancelled is True
        assert result.code is None

    def test_reset_command(self, sample_problem, capsys):
        """!reset should clear code."""
        inputs = ["def foo():", "!reset", "def bar():", "", ""]
        with patch("builtins.input", side_effect=inputs):
            result = read_user_code(sample_problem, Language.PYTHON)

        assert result.code is not None
        assert "def bar():" in result.code
        assert "def foo():" not in result.code
        captured = capsys.readouterr()
        assert "Code cleared" in captured.out

    def test_hint_command(self, sample_problem, capsys):
        """!hint should show hint."""
        inputs = ["!hint", "def solution(x): return x", "", ""]
        with patch("builtins.input", side_effect=inputs):
            result = read_user_code(sample_problem, Language.PYTHON)

        captured = capsys.readouterr()
        assert "Simple" in captured.out or "Hint" in captured.out

    def test_empty_input_is_cancelled(self, sample_problem):
        """Empty input should be treated as cancelled."""
        with patch("builtins.input", side_effect=["", ""]):
            result = read_user_code(sample_problem, Language.PYTHON)

        assert result.cancelled is True

    def test_eof_ends_input(self, sample_problem):
        """EOF should end input."""
        with patch("builtins.input", side_effect=["def foo():", EOFError]):
            result = read_user_code(sample_problem, Language.PYTHON)

        assert result.code is not None
        assert "def foo():" in result.code


class TestReadCodeFromFile:
    """Tests for read_code_from_file function."""

    def test_reads_file(self):
        """Should read code from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def solution(): pass")
            f.flush()
            path = f.name

        try:
            code = read_code_from_file(path)
            assert code == "def solution(): pass"
        finally:
            Path(path).unlink()

    def test_raises_on_missing_file(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            read_code_from_file("/nonexistent/path/file.py")


class TestAskContinue:
    """Tests for ask_continue function."""

    def test_yes_returns_true(self):
        """'y' should return True."""
        with patch("builtins.input", return_value="y"):
            assert ask_continue() is True

    def test_yes_full_returns_true(self):
        """'yes' should return True."""
        with patch("builtins.input", return_value="yes"):
            assert ask_continue() is True

    def test_empty_returns_true(self):
        """Empty input should return True."""
        with patch("builtins.input", return_value=""):
            assert ask_continue() is True

    def test_no_returns_false(self):
        """'n' should return False."""
        with patch("builtins.input", return_value="n"):
            assert ask_continue() is False

    def test_no_full_returns_false(self):
        """'no' should return False."""
        with patch("builtins.input", return_value="no"):
            assert ask_continue() is False

    def test_retries_on_invalid(self, capsys):
        """Should retry on invalid input."""
        with patch("builtins.input", side_effect=["maybe", "y"]):
            result = ask_continue()
        assert result is True
        captured = capsys.readouterr()
        assert "Enter y or n" in captured.out


class TestAskRetry:
    """Tests for ask_retry function."""

    def test_yes_returns_true(self):
        """'y' should return True."""
        with patch("builtins.input", return_value="y"):
            assert ask_retry() is True

    def test_no_returns_false(self):
        """'n' should return False."""
        with patch("builtins.input", return_value="n"):
            assert ask_retry() is False

    def test_empty_returns_true(self):
        """Empty input should return True."""
        with patch("builtins.input", return_value=""):
            assert ask_retry() is True
