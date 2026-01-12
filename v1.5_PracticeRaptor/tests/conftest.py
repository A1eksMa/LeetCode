"""Shared pytest fixtures."""
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

import pytest

# Add practiceraptor to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.domain.models import (
    Problem,
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
    User,
)
from core.domain.enums import Difficulty, Language


# ============================================================
# Temporary Directories
# ============================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_data_dir(temp_dir):
    """Create data subdirectories."""
    (temp_dir / "problems").mkdir()
    (temp_dir / "users").mkdir()
    (temp_dir / "drafts").mkdir()
    (temp_dir / "submissions").mkdir()
    (temp_dir / "progress").mkdir()
    return temp_dir


# ============================================================
# Domain Model Fixtures
# ============================================================

@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id=1,
        title=LocalizedText({"en": "Two Sum", "ru": "Сумма двух чисел"}),
        description=LocalizedText({
            "en": "Given an array of integers nums and an integer target...",
            "ru": "Дан массив целых чисел nums и целое число target...",
        }),
        difficulty=Difficulty.EASY,
        tags=("array", "hash-table"),
        examples=(
            Example(
                input={"nums": [2, 7, 11, 15], "target": 9},
                output=[0, 1],
                explanation=LocalizedText({"en": "nums[0] + nums[1] = 9"}),
            ),
        ),
        test_cases=(
            TestCase(
                input={"nums": [2, 7, 11, 15], "target": 9},
                expected=[0, 1],
                description="basic case",
            ),
            TestCase(
                input={"nums": [3, 2, 4], "target": 6},
                expected=[1, 2],
                description="answer not at start",
            ),
        ),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def two_sum(nums: list[int], target: int) -> list[int]:",
                solutions=(
                    Solution(
                        name="Hash Map",
                        complexity="O(n)",
                        code="""def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []""",
                    ),
                ),
            ),
        ),
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="test_user_123",
        locale="en",
        preferred_language=Language.PYTHON,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def correct_solution_code():
    """Correct solution code for two_sum."""
    return """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []"""


@pytest.fixture
def wrong_solution_code():
    """Wrong solution code for two_sum."""
    return """def two_sum(nums, target):
    return [0, 0]"""


@pytest.fixture
def syntax_error_code():
    """Code with syntax error."""
    return """def two_sum(nums, target)
    return nums"""


# ============================================================
# Repository Fixtures
# ============================================================

@pytest.fixture
def problem_repo(temp_data_dir, sample_problem):
    """Create JsonProblemRepository with sample data."""
    import json
    from adapters.storage.json_problem_repository import JsonProblemRepository

    # Write sample problem to JSON
    problem_data = {
        "id": sample_problem.id,
        "title": sample_problem.title.translations,
        "description": sample_problem.description.translations,
        "difficulty": sample_problem.difficulty.value,
        "tags": list(sample_problem.tags),
        "examples": [
            {
                "input": ex.input,
                "output": ex.output,
                "explanation": ex.explanation.translations if ex.explanation else None,
            }
            for ex in sample_problem.examples
        ],
        "test_cases": [
            {
                "input": tc.input,
                "expected": tc.expected,
                "description": tc.description,
            }
            for tc in sample_problem.test_cases
        ],
        "languages": {
            "python3": {
                "function_signature": sample_problem.languages[0].function_signature,
                "solutions": [
                    {
                        "name": s.name,
                        "complexity": s.complexity,
                        "code": s.code,
                    }
                    for s in sample_problem.languages[0].solutions
                ],
            }
        },
    }

    problems_dir = temp_data_dir / "problems"
    (problems_dir / "1_two_sum.json").write_text(
        json.dumps(problem_data, ensure_ascii=False, indent=2)
    )

    return JsonProblemRepository(problems_dir)


@pytest.fixture
def user_repo(temp_data_dir):
    """Create JsonUserRepository."""
    from adapters.storage.json_user_repository import JsonUserRepository
    return JsonUserRepository(temp_data_dir / "users")


@pytest.fixture
def draft_repo(temp_data_dir):
    """Create JsonDraftRepository."""
    from adapters.storage.json_draft_repository import JsonDraftRepository
    return JsonDraftRepository(temp_data_dir / "drafts")


@pytest.fixture
def submission_repo(temp_data_dir):
    """Create JsonSubmissionRepository."""
    from adapters.storage.json_submission_repository import JsonSubmissionRepository
    return JsonSubmissionRepository(temp_data_dir / "submissions")


@pytest.fixture
def progress_repo(temp_data_dir):
    """Create JsonProgressRepository."""
    from adapters.storage.json_progress_repository import JsonProgressRepository
    return JsonProgressRepository(temp_data_dir / "progress")


# ============================================================
# Executor Fixtures
# ============================================================

@pytest.fixture
def executor():
    """Create LocalExecutor for testing."""
    from adapters.executors.local_executor import LocalExecutor, ExecutorConfig
    return LocalExecutor(ExecutorConfig(timeout_sec=2))


# ============================================================
# Container Fixtures
# ============================================================

@pytest.fixture
def container(problem_repo, user_repo, draft_repo, submission_repo, progress_repo, executor):
    """Create a test container with all dependencies."""
    from di.container import Container
    from adapters.auth.anonymous_auth import AnonymousAuthProvider

    return Container(
        problem_repo=problem_repo,
        user_repo=user_repo,
        draft_repo=draft_repo,
        submission_repo=submission_repo,
        progress_repo=progress_repo,
        executor=executor,
        auth=AnonymousAuthProvider("test_user"),
        default_locale="en",
        default_timeout_sec=2,
    )


@pytest.fixture
def mock_container():
    """Create a mock container for unit tests."""
    container = MagicMock()
    container.default_locale = "en"
    container.problem_repo = MagicMock()
    container.executor = MagicMock()
    return container
