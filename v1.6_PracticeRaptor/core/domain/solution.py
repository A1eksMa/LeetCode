"""Solution-related domain models."""

from dataclasses import dataclass
from datetime import datetime

from .enums import Complexity, ProgrammingLanguage


@dataclass(frozen=True)
class Signature:
    """Function signature for a specific programming language.

    Provides the function template that user must implement.
    """

    problem_id: int
    programming_language: ProgrammingLanguage
    signature: str = ""


@dataclass(frozen=True)
class CanonicalSolution:
    """Reference solution for a specific programming language.

    Represents an official/canonical solution that can be shown
    to user after they solve the problem or request help.

    Multiple solutions per problem are supported (different approaches).

    Example:
        CanonicalSolution(
            canonical_solution_id=1,
            problem_id=1,
            programming_language=ProgrammingLanguage.PYTHON,
            name="Hash Map (One Pass)",
            complexity=Complexity.O_N,
            canonical_solution="def two_sum(...):\\n    ..."
        )
    """

    canonical_solution_id: int
    problem_id: int
    programming_language: ProgrammingLanguage
    name: str
    complexity: Complexity
    canonical_solution: str = ""


@dataclass(frozen=True)
class TestCase:
    """Test case as executable code for a specific language.

    Tests are language-specific executable code strings that
    are run by the executor microservice.

    Example:
        TestCase(
            test_case_id=1,
            problem_id=1,
            programming_language=ProgrammingLanguage.PYTHON,
            test='assert two_sum([2, 7, 11, 15], 9) == [0, 1]'
        )
    """

    test_case_id: int
    problem_id: int
    programming_language: ProgrammingLanguage
    test: str = ""


@dataclass(frozen=True)
class Solution:
    """Working solution object.

    Represents the complete working context for solving a problem:
    - Signature and canonical solutions (from problem definition)
    - User's code (initially empty, filled during solving)
    - Test cases: all and examples subset

    Usage:
        # Create from problem specification
        solution = Solution(
            problem_id=1,
            programming_language=ProgrammingLanguage.PYTHON,
            function_signature=signature,
            all_test_cases=all_tests,
            example_test_cases=example_tests,
        )

        # User writes code
        solution = replace(solution, code=user_code)

        # Quick check runs example_test_cases
        # Full submission runs all_test_cases
    """

    problem_id: int
    programming_language: ProgrammingLanguage
    function_signature: Signature
    canonical_solutions: tuple[CanonicalSolution, ...] = ()
    code: str = ""
    all_test_cases: tuple[TestCase, ...] = ()
    example_test_cases: tuple[TestCase, ...] = ()


@dataclass(frozen=True)
class Draft:
    """Saved snapshot of user's solution.

    Created on events: code check, program exit, manual save.
    Enables auto-save functionality and session recovery.

    Unique constraint: (user_id, problem_id, programming_language)
    Only one draft per user per problem per language.

    Note: Serialized to flat JSON for storage, but uses
    nested Solution in runtime for convenience.
    """

    draft_id: int
    user_id: int
    solution: Solution
    created_at: datetime
    updated_at: datetime
