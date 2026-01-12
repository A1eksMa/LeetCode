"""Code executor interfaces (Ports)."""
from typing import Protocol

from core.domain.models import TestCase, ExecutionResult
from core.domain.result import Result
from core.domain.errors import ExecutionError


class ICodeExecutor(Protocol):
    """Interface for code execution."""

    def execute(
        self,
        code: str,
        test_cases: tuple[TestCase, ...],
        function_name: str,
        timeout_sec: int = 5,
    ) -> Result[ExecutionResult, ExecutionError]:
        """
        Execute code against test cases.

        Args:
            code: User's code to execute
            test_cases: Test cases to run
            function_name: Name of the function to call
            timeout_sec: Maximum execution time per test

        Returns:
            Result with ExecutionResult on success or ExecutionError on failure
        """
        ...

    def validate_syntax(self, code: str) -> Result[None, ExecutionError]:
        """
        Check if code has valid syntax.

        Args:
            code: Code to validate

        Returns:
            Ok(None) if valid, Err(ExecutionError) if invalid
        """
        ...
