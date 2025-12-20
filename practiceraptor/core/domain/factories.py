"""Factory functions for creating domain objects."""
from datetime import datetime
from uuid import uuid4

from .models import User, Draft, Submission, Progress
from .enums import Language, ProgressStatus


def create_user(
    user_id: str | None = None,
    locale: str = "en",
    preferred_language: Language = Language.PYTHON,
) -> User:
    """Create a new user with defaults."""
    return User(
        id=user_id or str(uuid4()),
        locale=locale,
        preferred_language=preferred_language,
        created_at=datetime.now(),
    )


def create_draft(
    user_id: str,
    problem_id: int,
    code: str,
    language: Language = Language.PYTHON,
) -> Draft:
    """Create a new draft."""
    return Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )


def create_submission(
    user_id: str,
    problem_id: int,
    code: str,
    execution_time_ms: int,
    memory_used_kb: int = 0,
    language: Language = Language.PYTHON,
) -> Submission:
    """Create a new submission."""
    return Submission(
        id=str(uuid4()),
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        execution_time_ms=execution_time_ms,
        memory_used_kb=memory_used_kb,
        created_at=datetime.now(),
    )


def create_initial_progress(user_id: str, problem_id: int) -> Progress:
    """Create initial progress for a problem."""
    return Progress(
        user_id=user_id,
        problem_id=problem_id,
        status=ProgressStatus.NOT_STARTED,
        attempts=0,
        solved_languages=(),
        first_solved_at=None,
    )
