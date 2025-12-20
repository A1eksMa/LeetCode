"""Tests for execution service functions."""
import pytest

from core.services.execution import (
    validate_code_syntax,
    extract_function_name,
)


class TestValidateCodeSyntax:
    """Tests for validate_code_syntax function."""

    def test_valid_code_returns_ok(self) -> None:
        """Valid code should return Ok with the code."""
        code = "def solution(x): return x * 2"
        result = validate_code_syntax(code)
        assert result.is_ok()
        assert result.unwrap() == code

    def test_multiline_valid_code(self) -> None:
        """Multiline valid code should return Ok."""
        code = """def solution(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []"""
        result = validate_code_syntax(code)
        assert result.is_ok()

    def test_empty_code_returns_error(self) -> None:
        """Empty code should return error."""
        result = validate_code_syntax("")
        assert result.is_err()
        assert "empty" in result.error.message.lower()

    def test_whitespace_only_returns_error(self) -> None:
        """Whitespace-only code should return error."""
        result = validate_code_syntax("   \n\t  ")
        assert result.is_err()
        assert "empty" in result.error.message.lower()

    def test_syntax_error_returns_error(self) -> None:
        """Code with syntax error should return error."""
        code = "def solution(x) return x"  # missing colon
        result = validate_code_syntax(code)
        assert result.is_err()
        assert "syntax" in result.error.message.lower()

    def test_syntax_error_includes_line_number(self) -> None:
        """Syntax error message should include line number."""
        code = "x = 1\ny = 2\ndef broken( return"
        result = validate_code_syntax(code)
        assert result.is_err()
        assert "line" in result.error.message.lower()

    def test_field_is_code(self) -> None:
        """Error field should be 'code'."""
        result = validate_code_syntax("")
        assert result.is_err()
        assert result.error.field == "code"


class TestExtractFunctionName:
    """Tests for extract_function_name function."""

    def test_extracts_simple_name(self) -> None:
        """Extract name from simple signature."""
        sig = "def two_sum(nums, target):"
        assert extract_function_name(sig) == "two_sum"

    def test_extracts_name_with_types(self) -> None:
        """Extract name from typed signature."""
        sig = "def two_sum(nums: list[int], target: int) -> list[int]:"
        assert extract_function_name(sig) == "two_sum"

    def test_extracts_name_with_complex_types(self) -> None:
        """Extract name from signature with complex types."""
        sig = "def process(data: dict[str, list[tuple[int, ...]]]) -> None:"
        assert extract_function_name(sig) == "process"

    def test_returns_default_for_invalid(self) -> None:
        """Return 'solution' for invalid signature."""
        sig = "invalid"
        assert extract_function_name(sig) == "solution"

    def test_returns_default_for_empty(self) -> None:
        """Return 'solution' for empty string."""
        sig = ""
        assert extract_function_name(sig) == "solution"

    def test_handles_no_spaces(self) -> None:
        """Handle signature without spaces."""
        sig = "def func():"
        assert extract_function_name(sig) == "func"

    def test_handles_underscore_names(self) -> None:
        """Handle function names with underscores."""
        sig = "def _private_func(x):"
        assert extract_function_name(sig) == "_private_func"

    def test_handles_numbers_in_name(self) -> None:
        """Handle function names with numbers."""
        sig = "def solve2(x):"
        assert extract_function_name(sig) == "solve2"
