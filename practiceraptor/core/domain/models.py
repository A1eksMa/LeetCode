"""Domain models - immutable data structures."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import Difficulty, Language, ProgressStatus


# ============================================================
# Value Objects
# ============================================================

@dataclass(frozen=True)
class LocalizedText:
    """Text with translations."""
    translations: dict[str, str] = field(default_factory=dict)

    def get(self, locale: str, fallback: str = "en") -> str:
        """Get text for locale with fallback."""
        return self.translations.get(locale, self.translations.get(fallback, ""))

    def __str__(self) -> str:
        return self.get("en")


@dataclass(frozen=True)
class Example:
    """Problem example with input/output."""
    input: dict[str, Any]
    output: Any
    explanation: LocalizedText | None = None


@dataclass(frozen=True)
class TestCase:
    """Test case for validation."""
    input: dict[str, Any]
    expected: Any
    description: str | None = None
    is_hidden: bool = False


@dataclass(frozen=True)
class Solution:
    """Canonical/reference solution."""
    name: str
    complexity: str  # e.g., "O(n)"
    code: str


@dataclass(frozen=True)
class LanguageSpec:
    """Language-specific problem data."""
    language: Language
    function_signature: str
    solutions: tuple[Solution, ...] = ()


# ============================================================
# Entities
# ============================================================

@dataclass(frozen=True)
class Problem:
    """Coding problem entity."""
    id: int
    title: LocalizedText
    description: LocalizedText
    difficulty: Difficulty
    tags: tuple[str, ...] = ()
    examples: tuple[Example, ...] = ()
    test_cases: tuple[TestCase, ...] = ()
    languages: tuple[LanguageSpec, ...] = ()
    hints: tuple[LocalizedText, ...] = ()

    def get_language_spec(self, language: Language) -> LanguageSpec | None:
        """Get spec for specific language."""
        for spec in self.languages:
            if spec.language == language:
                return spec
        return None


@dataclass(frozen=True)
class User:
    """User entity."""
    id: str
    locale: str = "en"
    preferred_language: Language = Language.PYTHON
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())


@dataclass(frozen=True)
class Draft:
    """Unsaved user code."""
    user_id: str
    problem_id: int
    language: Language
    code: str
    updated_at: datetime


@dataclass(frozen=True)
class Submission:
    """Successful submission."""
    id: str
    user_id: str
    problem_id: int
    language: Language
    code: str
    execution_time_ms: int
    memory_used_kb: int
    created_at: datetime


@dataclass(frozen=True)
class Progress:
    """User progress on a problem."""
    user_id: str
    problem_id: int
    status: ProgressStatus
    attempts: int = 0
    solved_languages: tuple[Language, ...] = ()
    first_solved_at: datetime | None = None


# ============================================================
# Result Objects (for execution)
# ============================================================

@dataclass(frozen=True)
class TestResult:
    """Result of running a single test."""
    test_case: TestCase
    passed: bool
    actual: Any = None
    execution_time_ms: int = 0
    error_message: str | None = None


@dataclass(frozen=True)
class ExecutionResult:
    """Result of running all tests."""
    success: bool
    test_results: tuple[TestResult, ...] = ()
    total_time_ms: int = 0
    memory_used_kb: int = 0
    error: str | None = None

    @property
    def passed_count(self) -> int:
        """Count of passed tests."""
        return sum(1 for r in self.test_results if r.passed)

    @property
    def total_count(self) -> int:
        """Total number of tests."""
        return len(self.test_results)
