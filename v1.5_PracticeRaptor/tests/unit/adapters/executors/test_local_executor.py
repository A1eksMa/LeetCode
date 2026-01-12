"""Tests for LocalExecutor."""
import pytest

from adapters.executors.local_executor import LocalExecutor, ExecutorConfig
from core.domain.models import TestCase


@pytest.fixture
def executor() -> LocalExecutor:
    """Create executor with short timeout for tests."""
    return LocalExecutor(ExecutorConfig(timeout_sec=2))


@pytest.fixture
def simple_test_case() -> TestCase:
    """Create a simple test case."""
    return TestCase(
        input={"x": 5},
        expected=10,
    )


class TestValidateSyntax:
    """Tests for validate_syntax method."""

    def test_valid_code_returns_ok(self, executor: LocalExecutor) -> None:
        """Test that valid code returns Ok."""
        code = "def solution(x): return x * 2"

        result = executor.validate_syntax(code)

        assert result.is_ok()

    def test_multiline_valid_code_returns_ok(self, executor: LocalExecutor) -> None:
        """Test that multiline valid code returns Ok."""
        code = """
def solution(x):
    result = x * 2
    return result
"""
        result = executor.validate_syntax(code)

        assert result.is_ok()

    def test_invalid_code_returns_error(self, executor: LocalExecutor) -> None:
        """Test that invalid code returns error."""
        code = "def solution(x) return x"  # Missing colon

        result = executor.validate_syntax(code)

        assert result.is_err()
        assert result.error.error_type == "syntax"

    def test_empty_code_returns_ok(self, executor: LocalExecutor) -> None:
        """Test that empty code is valid syntax."""
        code = ""

        result = executor.validate_syntax(code)

        assert result.is_ok()


class TestExecute:
    """Tests for execute method."""

    def test_correct_solution_passes(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that correct solution passes."""
        code = "def solution(x): return x * 2"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is True
        assert exec_result.passed_count == 1
        assert exec_result.test_results[0].passed is True

    def test_wrong_answer_fails(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that wrong answer fails."""
        code = "def solution(x): return x + 1"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert exec_result.test_results[0].passed is False
        assert exec_result.test_results[0].actual == 6

    def test_multiple_test_cases_all_pass(self, executor: LocalExecutor) -> None:
        """Test that all test cases can pass."""
        code = "def double(x): return x * 2"
        test_cases = (
            TestCase(input={"x": 1}, expected=2),
            TestCase(input={"x": 5}, expected=10),
            TestCase(input={"x": 0}, expected=0),
        )

        result = executor.execute(
            code=code,
            test_cases=test_cases,
            function_name="double",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is True
        assert exec_result.passed_count == 3

    def test_stops_on_first_failure(self, executor: LocalExecutor) -> None:
        """Test that execution stops on first failure."""
        code = "def solution(x): return x"
        test_cases = (
            TestCase(input={"x": 1}, expected=1),  # Pass
            TestCase(input={"x": 2}, expected=99),  # Fail
            TestCase(input={"x": 3}, expected=3),  # Would pass but not run
        )

        result = executor.execute(
            code=code,
            test_cases=test_cases,
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert len(exec_result.test_results) == 2  # Only 2 tests ran

    def test_timeout_is_handled(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that timeout is properly handled."""
        code = """
def solution(x):
    while True:
        pass
    return x
"""
        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
            timeout_sec=1,
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert "timeout" in exec_result.test_results[0].error_message.lower()

    def test_runtime_error_is_captured(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that runtime errors are captured."""
        code = "def solution(x): return 1 / 0"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert "ZeroDivision" in exec_result.test_results[0].error_message

    def test_missing_function_is_error(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that missing function is reported as error."""
        code = "def other_func(x): return x"

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        assert "not found" in exec_result.test_results[0].error_message.lower()

    def test_syntax_error_returns_err(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that syntax error returns Err result."""
        code = "def solution(x) return x"  # Missing colon

        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_err()
        assert result.error.error_type == "syntax"

    def test_multiple_arguments(self, executor: LocalExecutor) -> None:
        """Test function with multiple arguments."""
        code = """
def add(a, b):
    return a + b
"""
        test_case = TestCase(
            input={"a": 2, "b": 3},
            expected=5,
        )

        result = executor.execute(
            code=code,
            test_cases=(test_case,),
            function_name="add",
        )

        assert result.is_ok()
        assert result.unwrap().success is True

    def test_list_result(self, executor: LocalExecutor) -> None:
        """Test function returning list."""
        code = "def solution(nums): return sorted(nums)"
        test_case = TestCase(
            input={"nums": [3, 1, 2]},
            expected=[1, 2, 3],
        )

        result = executor.execute(
            code=code,
            test_cases=(test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        assert result.unwrap().success is True

    def test_dict_result(self, executor: LocalExecutor) -> None:
        """Test function returning dict."""
        code = "def solution(x): return {'value': x * 2}"
        test_case = TestCase(
            input={"x": 5},
            expected={"value": 10},
        )

        result = executor.execute(
            code=code,
            test_cases=(test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        assert result.unwrap().success is True


class TestFloatComparison:
    """Tests for float comparison with tolerance."""

    def test_exact_float_passes(self, executor: LocalExecutor) -> None:
        """Test that exact float match passes."""
        code = "def solution(x): return x / 2.0"
        test_case = TestCase(input={"x": 10}, expected=5.0)

        result = executor.execute(
            code=code,
            test_cases=(test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        assert result.unwrap().success is True

    def test_float_within_tolerance_passes(self, executor: LocalExecutor) -> None:
        """Test that float within tolerance passes."""
        code = "def solution(x): return x / 3.0"
        # 10/3 = 3.3333... but we compare with tolerance
        test_case = TestCase(input={"x": 10}, expected=3.3333333333333335)

        result = executor.execute(
            code=code,
            test_cases=(test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        assert result.unwrap().success is True


class TestSandbox:
    """Tests for sandbox security."""

    def test_cannot_import(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that import is blocked."""
        code = """
import os
def solution(x):
    return x
"""
        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False
        # Import should fail since __import__ is not available

    def test_cannot_access_file_system(
        self, executor: LocalExecutor, simple_test_case: TestCase
    ) -> None:
        """Test that file system access is blocked."""
        code = """
def solution(x):
    open('/etc/passwd', 'r')
    return x
"""
        result = executor.execute(
            code=code,
            test_cases=(simple_test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        exec_result = result.unwrap()
        assert exec_result.success is False


class TestExecutorConfig:
    """Tests for ExecutorConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ExecutorConfig()

        assert config.timeout_sec == 5
        assert config.memory_limit_mb == 256

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ExecutorConfig(timeout_sec=10, memory_limit_mb=512)

        assert config.timeout_sec == 10
        assert config.memory_limit_mb == 512

    def test_executor_uses_config_timeout(self) -> None:
        """Test that executor respects config timeout."""
        config = ExecutorConfig(timeout_sec=1)
        executor = LocalExecutor(config)

        code = "def solution(x):\n    import time; time.sleep(5)\n    return x"
        test_case = TestCase(input={"x": 1}, expected=1)

        result = executor.execute(
            code=code,
            test_cases=(test_case,),
            function_name="solution",
        )

        assert result.is_ok()
        assert result.unwrap().success is False
        # Should timeout quickly since config has 1 second timeout
