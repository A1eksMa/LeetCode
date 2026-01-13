"""Domain layer - pure business logic and data structures.

This module provides the public API for the domain layer.
All models can be imported directly from core.domain:

    from core.domain import Problem, User, Settings

Or from specific modules:

    from core.domain.problem import Problem
    from core.domain.user import User, DEFAULT_USER
"""

# Enums
from .enums import (
    Category,
    Complexity,
    Difficulty,
    Language,
    ProgrammingLanguage,
    ProblemStatus,
    ExecutionStatus,
    TextEditor,
)

# Localized content
from .localization import (
    Description,
    Editorial,
    Explanation,
    Hint,
    Tag,
    Title,
)

# Problem-related
from .problem import (
    Example,
    Problem,
    ProblemDescription,
    ProblemSelector,
)

# User management
from .user import DEFAULT_USER, User
from .settings import DEFAULT_SETTINGS, Settings

# Solution and testing
from .solution import (
    CanonicalSolution,
    Draft,
    Signature,
    Solution,
    TestCase,
)

# Execution results
from .execution import (
    Execution,
    Submission,
    TestResult,
)

# Result type (functional error handling)
from .result import Err, Ok, Result

# Domain errors
from .errors import (
    DomainError,
    ExecutionError,
    NotFoundError,
    StorageError,
    ValidationError,
)

__all__ = [
    # Enums
    "Category",
    "Complexity",
    "Difficulty",
    "Language",
    "ProgrammingLanguage",
    "ProblemStatus",
    "ExecutionStatus",
    "TextEditor",
    # Localized content
    "Description",
    "Editorial",
    "Explanation",
    "Hint",
    "Tag",
    "Title",
    # Problem-related
    "Example",
    "Problem",
    "ProblemDescription",
    "ProblemSelector",
    # User management
    "DEFAULT_SETTINGS",
    "DEFAULT_USER",
    "Settings",
    "User",
    # Solution and testing
    "CanonicalSolution",
    "Draft",
    "Signature",
    "Solution",
    "TestCase",
    # Execution results
    "Execution",
    "Submission",
    "TestResult",
    # Result type
    "Err",
    "Ok",
    "Result",
    # Domain errors
    "DomainError",
    "ExecutionError",
    "NotFoundError",
    "StorageError",
    "ValidationError",
]
