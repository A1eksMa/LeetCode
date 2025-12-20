"""Domain layer - models, enums, errors, result type."""
from .enums import Difficulty, Language, SubmissionStatus, ProgressStatus
from .errors import (
    DomainError,
    NotFoundError,
    ValidationError,
    ExecutionError,
    StorageError,
)
from .result import Ok, Err, Result
from .models import (
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
    Problem,
    User,
    Draft,
    Submission,
    Progress,
    TestResult,
    ExecutionResult,
)
from .factories import (
    create_user,
    create_draft,
    create_submission,
    create_initial_progress,
)

__all__ = [
    # Enums
    "Difficulty",
    "Language",
    "SubmissionStatus",
    "ProgressStatus",
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
    # Models
    "LocalizedText",
    "Example",
    "TestCase",
    "Solution",
    "LanguageSpec",
    "Problem",
    "User",
    "Draft",
    "Submission",
    "Progress",
    "TestResult",
    "ExecutionResult",
    # Factories
    "create_user",
    "create_draft",
    "create_submission",
    "create_initial_progress",
]
