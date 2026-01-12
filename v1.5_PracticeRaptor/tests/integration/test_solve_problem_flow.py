"""Integration tests for the complete problem-solving flow."""
import pytest

from core.services import (
    get_problem,
    validate_code_syntax,
    run_full_tests,
)
from core.domain.enums import Language


class TestSolveProblemFlow:
    """Test the complete flow of solving a problem."""

    def test_correct_solution_passes_all_tests(
        self,
        problem_repo,
        executor,
        correct_solution_code,
    ):
        """A correct solution should pass all test cases."""
        # Get problem
        result = get_problem(1, problem_repo)
        assert result.is_ok()
        problem = result.unwrap()

        # Validate syntax
        syntax_result = validate_code_syntax(correct_solution_code)
        assert syntax_result.is_ok()

        # Run tests
        exec_result = run_full_tests(
            code=correct_solution_code,
            problem=problem,
            language=Language.PYTHON,
            executor=executor,
        )

        assert exec_result.is_ok()
        result = exec_result.unwrap()
        assert result.success is True
        assert result.passed_count == result.total_count

    def test_wrong_solution_fails(
        self,
        problem_repo,
        executor,
        wrong_solution_code,
    ):
        """A wrong solution should fail tests."""
        result = get_problem(1, problem_repo)
        problem = result.unwrap()

        exec_result = run_full_tests(
            code=wrong_solution_code,
            problem=problem,
            language=Language.PYTHON,
            executor=executor,
        )

        assert exec_result.is_ok()
        result = exec_result.unwrap()
        assert result.success is False

    def test_syntax_error_is_caught(
        self,
        syntax_error_code,
    ):
        """Syntax errors should be caught before execution."""
        result = validate_code_syntax(syntax_error_code)

        assert result.is_err()
        # Access error via .error attribute
        assert "syntax" in result.error.message.lower() or "Syntax" in result.error.message

    def test_timeout_is_handled(
        self,
        problem_repo,
        executor,
    ):
        """Infinite loops should timeout."""
        result = get_problem(1, problem_repo)
        problem = result.unwrap()

        infinite_loop_code = """
def two_sum(nums, target):
    while True:
        pass
"""

        exec_result = run_full_tests(
            code=infinite_loop_code,
            problem=problem,
            language=Language.PYTHON,
            executor=executor,
        )

        assert exec_result.is_ok()
        result = exec_result.unwrap()
        assert result.success is False
        assert result.test_results[0].error_message is not None
        assert "timeout" in result.test_results[0].error_message.lower()

    def test_runtime_error_is_captured(
        self,
        problem_repo,
        executor,
    ):
        """Runtime errors should be captured and reported."""
        result = get_problem(1, problem_repo)
        problem = result.unwrap()

        error_code = """
def two_sum(nums, target):
    return 1 / 0
"""

        exec_result = run_full_tests(
            code=error_code,
            problem=problem,
            language=Language.PYTHON,
            executor=executor,
        )

        assert exec_result.is_ok()
        result = exec_result.unwrap()
        assert result.success is False
        assert result.test_results[0].error_message is not None
        assert "ZeroDivision" in result.test_results[0].error_message


class TestProgressTracking:
    """Test progress tracking through the flow."""

    def test_progress_updates_on_attempt(
        self,
        progress_repo,
    ):
        """Progress should update when user attempts a problem."""
        from core.services import get_user_progress, update_progress_on_attempt
        from core.domain.enums import ProgressStatus, Language

        user_id = "test_user"
        problem_id = 1

        # Initial progress
        progress = get_user_progress(user_id, problem_id, progress_repo)
        assert progress.status == ProgressStatus.NOT_STARTED
        assert progress.attempts == 0

        # First failed attempt (use 'solved' not 'success')
        updated = update_progress_on_attempt(
            progress=progress,
            solved=False,
            language=Language.PYTHON,
        )
        assert updated.status == ProgressStatus.IN_PROGRESS
        assert updated.attempts == 1

        # Second successful attempt
        updated2 = update_progress_on_attempt(
            progress=updated,
            solved=True,
            language=Language.PYTHON,
        )
        assert updated2.status == ProgressStatus.SOLVED
        assert updated2.attempts == 2
        assert Language.PYTHON in updated2.solved_languages


class TestDraftPersistence:
    """Test draft saving and loading."""

    def test_save_and_load_draft(
        self,
        draft_repo,
    ):
        """Drafts should persist and load correctly."""
        from core.services import save_draft, get_draft
        from core.domain.enums import Language

        user_id = "test_user"
        problem_id = 1
        code = "def two_sum(nums, target): pass"

        # Save draft (use draft_repo not repo)
        result = save_draft(
            user_id=user_id,
            problem_id=problem_id,
            language=Language.PYTHON,
            code=code,
            draft_repo=draft_repo,
        )

        assert result.is_ok()
        draft = result.unwrap()
        assert draft.code == code

        # Load draft
        loaded_result = get_draft(user_id, problem_id, Language.PYTHON, draft_repo)
        assert loaded_result.is_ok()
        loaded = loaded_result.unwrap()
        assert loaded.code == code

    def test_draft_not_found_returns_err(
        self,
        draft_repo,
    ):
        """Loading non-existent draft should return Err."""
        from core.services import get_draft
        from core.domain.enums import Language

        result = get_draft("unknown_user", 999, Language.PYTHON, draft_repo)
        # Returns Err, not None
        assert result.is_err()
