"""Domain enumerations."""
from enum import Enum


class Difficulty(str, Enum):
    """Problem difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python3"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"


class SubmissionStatus(str, Enum):
    """Status of a submission."""
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"


class ProgressStatus(str, Enum):
    """User progress on a problem."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
