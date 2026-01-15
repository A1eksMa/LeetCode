"""Domain models - rich objects for business logic."""

from .enums import (
    Category,
    Complexity,
    Difficulty,
    ExecutionStatus,
    Language,
    ProblemStatus,
    ProgrammingLanguage,
    TextEditor,
)
from .localization import LocalizedText
from .problem import Example, Problem, ProblemSummary
from .solution import CanonicalSolution, Signature, Solution, TestCase
from .user import User, DEFAULT_USER
from .settings import Settings, DEFAULT_SETTINGS
from .execution import TestResult, Execution, Submission, Draft

__all__ = [
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
