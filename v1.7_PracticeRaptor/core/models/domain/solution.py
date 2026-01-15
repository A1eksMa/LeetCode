"""Solution domain models - working objects for problem solving."""

from dataclasses import dataclass, replace

from .enums import Complexity, ProgrammingLanguage


@dataclass(frozen=True)
class Signature:
    """Function signature template for a programming language.

    Provides the function stub that user must implement.

    Example:
        sig = Signature(
            language=ProgrammingLanguage.PYTHON,
            signature="def two_sum(nums: list[int], target: int) -> list[int]:",
        )
    """

    language: ProgrammingLanguage
    signature: str


@dataclass(frozen=True)
class TestCase:
    """Executable test case.

    Test is a code string executed by the executor service.
    Language-specific.

    Example:
        test = TestCase(
            language=ProgrammingLanguage.PYTHON,
            test="assert two_sum([2, 7, 11, 15], 9) == [0, 1]",
            is_example=True,
        )
    """

    language: ProgrammingLanguage
    test: str
    is_example: bool = False  # True = shown in problem description


@dataclass(frozen=True)
class CanonicalSolution:
    """Reference solution (shown after solving or on request).

    Multiple solutions per problem supported (different approaches).

    Example:
        sol = CanonicalSolution(
            language=ProgrammingLanguage.PYTHON,
            name="Hash Map (One Pass)",
            complexity=Complexity.O_N,
            code="def two_sum(nums, target):\\n    seen = {}\\n    ...",
        )
    """

    language: ProgrammingLanguage
    name: str  # Approach name: "Hash Map", "Two Pointers", etc.
    complexity: Complexity
    code: str


@dataclass(frozen=True)
class Solution:
    """Working solution context for problem solving.

    Aggregates everything needed to solve a problem:
    - Function signature (what to implement)
    - Test cases (for validation)
    - Canonical solutions (for reference after solving)
    - User's code (filled during solving)

    Example:
        solution = Solution(
            problem_id=1,
            language=ProgrammingLanguage.PYTHON,
            signature=Signature(...),
            test_cases=(...),
            canonical_solutions=(...),
        )

        # User writes code
        solution = solution.with_code("def two_sum(nums, target): ...")

        # Run example tests (quick check)
        example_tests = solution.example_tests

        # Run all tests (full submission)
        all_tests = solution.test_cases
    """

    problem_id: int
    language: ProgrammingLanguage
    signature: Signature
    test_cases: tuple[TestCase, ...] = ()
    canonical_solutions: tuple[CanonicalSolution, ...] = ()
    code: str = ""

    @property
    def example_tests(self) -> tuple[TestCase, ...]:
        """Get only example test cases (for quick check)."""
        return tuple(t for t in self.test_cases if t.is_example)

    @property
    def hidden_tests(self) -> tuple[TestCase, ...]:
        """Get only hidden test cases."""
        return tuple(t for t in self.test_cases if not t.is_example)


    def with_code(self, code: str) -> "Solution":
        """Return new Solution with updated code."""
        return replace(self, code=code)
