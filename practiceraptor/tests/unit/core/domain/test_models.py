"""Tests for domain models."""
import pytest
from datetime import datetime

from core.domain.models import (
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
from core.domain.enums import Difficulty, Language, ProgressStatus


class TestLocalizedText:
    def test_get_returns_translation(self) -> None:
        text = LocalizedText({"en": "Hello", "ru": "Привет"})
        assert text.get("en") == "Hello"
        assert text.get("ru") == "Привет"

    def test_get_falls_back_to_english(self) -> None:
        text = LocalizedText({"en": "Hello"})
        assert text.get("fr") == "Hello"

    def test_get_returns_empty_if_no_fallback(self) -> None:
        text = LocalizedText({"ru": "Привет"})
        assert text.get("fr") == ""

    def test_str_returns_english(self) -> None:
        text = LocalizedText({"en": "Hello", "ru": "Привет"})
        assert str(text) == "Hello"

    def test_empty_translations(self) -> None:
        text = LocalizedText()
        assert text.get("en") == ""


class TestExample:
    def test_creation(self) -> None:
        example = Example(
            input={"x": 1},
            output=2,
            explanation=LocalizedText({"en": "1 + 1 = 2"}),
        )
        assert example.input == {"x": 1}
        assert example.output == 2
        assert example.explanation is not None

    def test_without_explanation(self) -> None:
        example = Example(input={"x": 1}, output=2)
        assert example.explanation is None


class TestTestCase:
    def test_creation(self) -> None:
        tc = TestCase(
            input={"nums": [1, 2, 3]},
            expected=[1, 2, 3],
            description="basic case",
            is_hidden=True,
        )
        assert tc.input == {"nums": [1, 2, 3]}
        assert tc.expected == [1, 2, 3]
        assert tc.description == "basic case"
        assert tc.is_hidden is True

    def test_defaults(self) -> None:
        tc = TestCase(input={"x": 1}, expected=2)
        assert tc.description is None
        assert tc.is_hidden is False


class TestSolution:
    def test_creation(self) -> None:
        solution = Solution(
            name="Hash Map",
            complexity="O(n)",
            code="def solve(): pass",
        )
        assert solution.name == "Hash Map"
        assert solution.complexity == "O(n)"
        assert solution.code == "def solve(): pass"


class TestLanguageSpec:
    def test_creation(self) -> None:
        spec = LanguageSpec(
            language=Language.PYTHON,
            function_signature="def solve(x: int) -> int:",
            solutions=(
                Solution(name="Simple", complexity="O(1)", code="pass"),
            ),
        )
        assert spec.language == Language.PYTHON
        assert len(spec.solutions) == 1

    def test_empty_solutions(self) -> None:
        spec = LanguageSpec(
            language=Language.GO,
            function_signature="func solve(x int) int",
        )
        assert spec.solutions == ()


class TestProblem:
    @pytest.fixture
    def sample_problem(self) -> Problem:
        return Problem(
            id=1,
            title=LocalizedText({"en": "Two Sum"}),
            description=LocalizedText({"en": "Find two numbers..."}),
            difficulty=Difficulty.EASY,
            tags=("array", "hash-table"),
            examples=(
                Example(input={"nums": [2, 7], "target": 9}, output=[0, 1]),
            ),
            test_cases=(
                TestCase(input={"nums": [2, 7], "target": 9}, expected=[0, 1]),
            ),
            languages=(
                LanguageSpec(
                    language=Language.PYTHON,
                    function_signature="def two_sum(nums, target):",
                    solutions=(),
                ),
            ),
        )

    def test_get_language_spec_returns_spec(self, sample_problem: Problem) -> None:
        spec = sample_problem.get_language_spec(Language.PYTHON)
        assert spec is not None
        assert spec.language == Language.PYTHON

    def test_get_language_spec_returns_none_if_not_found(self, sample_problem: Problem) -> None:
        spec = sample_problem.get_language_spec(Language.GO)
        assert spec is None

    def test_defaults(self) -> None:
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Test"}),
            description=LocalizedText({"en": "Desc"}),
            difficulty=Difficulty.MEDIUM,
        )
        assert problem.tags == ()
        assert problem.examples == ()
        assert problem.hints == ()


class TestUser:
    def test_creation(self) -> None:
        user = User(
            id="user123",
            locale="ru",
            preferred_language=Language.GO,
            created_at=datetime(2024, 1, 1),
        )
        assert user.id == "user123"
        assert user.locale == "ru"
        assert user.preferred_language == Language.GO

    def test_defaults(self) -> None:
        user = User(id="user123")
        assert user.locale == "en"
        assert user.preferred_language == Language.PYTHON
        assert user.created_at is not None

    def test_auto_created_at(self) -> None:
        before = datetime.now()
        user = User(id="user123")
        after = datetime.now()
        assert user.created_at is not None
        assert before <= user.created_at <= after


class TestDraft:
    def test_creation(self) -> None:
        draft = Draft(
            user_id="user123",
            problem_id=1,
            language=Language.PYTHON,
            code="def solve(): pass",
            updated_at=datetime.now(),
        )
        assert draft.user_id == "user123"
        assert draft.problem_id == 1


class TestSubmission:
    def test_creation(self) -> None:
        submission = Submission(
            id="sub123",
            user_id="user123",
            problem_id=1,
            language=Language.PYTHON,
            code="def solve(): return 42",
            execution_time_ms=10,
            memory_used_kb=1024,
            created_at=datetime.now(),
        )
        assert submission.execution_time_ms == 10
        assert submission.memory_used_kb == 1024


class TestProgress:
    def test_creation(self) -> None:
        progress = Progress(
            user_id="user123",
            problem_id=1,
            status=ProgressStatus.SOLVED,
            attempts=3,
            solved_languages=(Language.PYTHON, Language.GO),
            first_solved_at=datetime.now(),
        )
        assert progress.status == ProgressStatus.SOLVED
        assert len(progress.solved_languages) == 2

    def test_defaults(self) -> None:
        progress = Progress(
            user_id="user123",
            problem_id=1,
            status=ProgressStatus.NOT_STARTED,
        )
        assert progress.attempts == 0
        assert progress.solved_languages == ()
        assert progress.first_solved_at is None


class TestTestResult:
    def test_passed(self) -> None:
        tc = TestCase(input={"x": 1}, expected=2)
        result = TestResult(
            test_case=tc,
            passed=True,
            actual=2,
            execution_time_ms=5,
        )
        assert result.passed is True
        assert result.error_message is None

    def test_failed(self) -> None:
        tc = TestCase(input={"x": 1}, expected=2)
        result = TestResult(
            test_case=tc,
            passed=False,
            actual=3,
            error_message="Expected 2, got 3",
        )
        assert result.passed is False
        assert result.error_message is not None


class TestExecutionResult:
    def test_success(self) -> None:
        tc = TestCase(input={"x": 1}, expected=2)
        result = ExecutionResult(
            success=True,
            test_results=(
                TestResult(test_case=tc, passed=True),
                TestResult(test_case=tc, passed=True),
            ),
            total_time_ms=10,
        )
        assert result.success is True
        assert result.passed_count == 2
        assert result.total_count == 2

    def test_failure(self) -> None:
        tc = TestCase(input={"x": 1}, expected=2)
        result = ExecutionResult(
            success=False,
            test_results=(
                TestResult(test_case=tc, passed=True),
                TestResult(test_case=tc, passed=False),
            ),
            total_time_ms=10,
        )
        assert result.success is False
        assert result.passed_count == 1
        assert result.total_count == 2

    def test_empty(self) -> None:
        result = ExecutionResult(success=True)
        assert result.passed_count == 0
        assert result.total_count == 0


class TestImmutability:
    def test_problem_is_frozen(self) -> None:
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Test"}),
            description=LocalizedText({"en": "Desc"}),
            difficulty=Difficulty.EASY,
        )
        with pytest.raises(AttributeError):
            problem.id = 2  # type: ignore

    def test_user_is_frozen(self) -> None:
        user = User(id="user123")
        with pytest.raises(AttributeError):
            user.locale = "ru"  # type: ignore

    def test_submission_is_frozen(self) -> None:
        submission = Submission(
            id="sub123",
            user_id="user123",
            problem_id=1,
            language=Language.PYTHON,
            code="pass",
            execution_time_ms=10,
            memory_used_kb=1024,
            created_at=datetime.now(),
        )
        with pytest.raises(AttributeError):
            submission.code = "new code"  # type: ignore
