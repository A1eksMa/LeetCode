"""Factory functions for creating test data."""
from datetime import datetime
from uuid import uuid4

from core.domain.models import (
    Problem,
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
    User,
    Draft,
    Submission,
    Progress,
)
from core.domain.enums import Difficulty, Language, ProgressStatus


def create_problem(
    id: int = 1,
    title: str = "Test Problem",
    difficulty: Difficulty = Difficulty.EASY,
    tags: tuple[str, ...] = ("test",),
    with_solutions: bool = True,
) -> Problem:
    """Create a problem for testing."""
    solutions: tuple[Solution, ...] = ()
    if with_solutions:
        solutions = (
            Solution(
                name="Brute Force",
                complexity="O(n^2)",
                code="def solution(x): return x",
            ),
        )

    return Problem(
        id=id,
        title=LocalizedText({"en": title}),
        description=LocalizedText({"en": f"Description for {title}"}),
        difficulty=difficulty,
        tags=tags,
        examples=(
            Example(
                input={"x": 1},
                output=2,
            ),
        ),
        test_cases=(
            TestCase(
                input={"x": 1},
                expected=2,
            ),
        ),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def solution(x: int) -> int:",
                solutions=solutions,
            ),
        ),
    )


def create_user(
    user_id: str | None = None,
    locale: str = "en",
    language: Language = Language.PYTHON,
) -> User:
    """Create a user for testing."""
    return User(
        id=user_id or f"user_{uuid4().hex[:8]}",
        locale=locale,
        preferred_language=language,
        created_at=datetime.now(),
    )


def create_draft(
    user_id: str = "test_user",
    problem_id: int = 1,
    code: str = "def solution(x): pass",
    language: Language = Language.PYTHON,
) -> Draft:
    """Create a draft for testing."""
    return Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )


def create_submission(
    user_id: str = "test_user",
    problem_id: int = 1,
    code: str = "def solution(x): return x * 2",
    execution_time_ms: int = 10,
) -> Submission:
    """Create a submission for testing."""
    return Submission(
        id=str(uuid4()),
        user_id=user_id,
        problem_id=problem_id,
        language=Language.PYTHON,
        code=code,
        execution_time_ms=execution_time_ms,
        memory_used_kb=1024,
        created_at=datetime.now(),
    )


def create_progress(
    user_id: str = "test_user",
    problem_id: int = 1,
    status: ProgressStatus = ProgressStatus.NOT_STARTED,
    attempts: int = 0,
) -> Progress:
    """Create progress for testing."""
    return Progress(
        user_id=user_id,
        problem_id=problem_id,
        status=status,
        attempts=attempts,
        solved_languages=(),
    )
