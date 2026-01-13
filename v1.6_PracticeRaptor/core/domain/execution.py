"""Execution-related domain models."""

from dataclasses import dataclass
from datetime import datetime

from .enums import ExecutionStatus
from .solution import Solution, TestCase


@dataclass(frozen=True)
class TestResult:
    """Result of executing a single test case."""

    test_case: TestCase
    result: ExecutionStatus
    error_message: str | None = None
    test_time_ms: int = 0
    test_memory_used_kb: int = 0


@dataclass(frozen=True)
class Execution:
    """Result of executing solution against test cases.

    Contains aggregated results of running all tests.
    """

    solution: Solution
    total_time_ms: int = 0
    memory_used_kb: int = 0
    test_results: tuple[TestResult, ...] = ()
    error_message: str | None = None
    result: ExecutionStatus = ExecutionStatus.ACCEPTED

    @property
    def passed_count(self) -> int:
        """Count of passed tests."""
        return sum(
            1 for r in self.test_results if r.result == ExecutionStatus.ACCEPTED
        )

    @property
    def total_count(self) -> int:
        """Total number of tests run."""
        return len(self.test_results)

    @property
    def is_accepted(self) -> bool:
        """Check if all tests passed."""
        return self.result == ExecutionStatus.ACCEPTED


@dataclass(frozen=True)
class Submission:
    """Successful submission record.

    Only accepted submissions are stored.
    Statistics are computed from submissions table.
    """

    submission_id: int
    created_at: datetime
    execution: Execution
