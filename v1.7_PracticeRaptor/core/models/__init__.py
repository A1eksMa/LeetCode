"""Core models - domain models, errors, and result types."""

from .errors import (
    DomainError,
    NotFoundError,
    ValidationError,
    ExecutionError,
    StorageError,
)
from .result import Ok, Err, Result

from .domain import (
    # Enums
    Category,
    Complexity,
    Difficulty,
    ExecutionStatus,
    Language,
    ProblemStatus,
    ProgrammingLanguage,
    TextEditor,
    # Localization
    LocalizedText,
    # Problem
    Example,
    Problem,
    ProblemSummary,
    # Solution
    CanonicalSolution,
    Signature,
    Solution,
    TestCase,
    # User
    User,
    DEFAULT_USER,
    # Settings
    Settings,
    DEFAULT_SETTINGS,
    # Execution
    TestResult,
    Execution,
    Submission,
    Draft,
)

__all__ = [
    # Errors
    "DomainError",
    "NotFoundError",
    "ValidationError",
    "ExecutionError",
    "StorageError",
    # Result
    "Ok",
    "Err",
    "Result",
    # Enums
    "Category",
    "Complexity",
    "Difficulty",
    "ExecutionStatus",
    "Language",
    "ProblemStatus",
    "ProgrammingLanguage",
    "TextEditor",
    # Localization
    "LocalizedText",
    # Problem
    "Example",
    "Problem",
    "ProblemSummary",
    # Solution
    "CanonicalSolution",
    "Signature",
    "Solution",
    "TestCase",
    # User
    "User",
    "DEFAULT_USER",
    # Settings
    "Settings",
    "DEFAULT_SETTINGS",
    # Execution
    "TestResult",
    "Execution",
    "Submission",
    "Draft",
]
