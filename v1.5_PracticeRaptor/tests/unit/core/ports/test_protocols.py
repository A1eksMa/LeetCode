"""Tests for port protocols."""
from typing import get_type_hints
import inspect

from core.ports import (
    IProblemRepository,
    IUserRepository,
    IDraftRepository,
    ISubmissionRepository,
    IProgressRepository,
    ICodeExecutor,
    IAuthProvider,
    AuthError,
)
from core.domain.errors import DomainError


class TestIProblemRepository:
    """Verify IProblemRepository protocol."""

    def test_has_get_by_id_method(self) -> None:
        assert hasattr(IProblemRepository, 'get_by_id')
        sig = inspect.signature(IProblemRepository.get_by_id)
        assert 'problem_id' in sig.parameters

    def test_has_get_all_method(self) -> None:
        assert hasattr(IProblemRepository, 'get_all')

    def test_has_filter_method(self) -> None:
        assert hasattr(IProblemRepository, 'filter')
        sig = inspect.signature(IProblemRepository.filter)
        assert 'difficulty' in sig.parameters
        assert 'tags' in sig.parameters
        assert 'language' in sig.parameters

    def test_has_count_method(self) -> None:
        assert hasattr(IProblemRepository, 'count')


class TestIUserRepository:
    """Verify IUserRepository protocol."""

    def test_has_get_by_id_method(self) -> None:
        assert hasattr(IUserRepository, 'get_by_id')

    def test_has_save_method(self) -> None:
        assert hasattr(IUserRepository, 'save')

    def test_has_delete_method(self) -> None:
        assert hasattr(IUserRepository, 'delete')


class TestIDraftRepository:
    """Verify IDraftRepository protocol."""

    def test_has_get_method(self) -> None:
        assert hasattr(IDraftRepository, 'get')
        sig = inspect.signature(IDraftRepository.get)
        assert 'user_id' in sig.parameters
        assert 'problem_id' in sig.parameters
        assert 'language' in sig.parameters

    def test_has_save_method(self) -> None:
        assert hasattr(IDraftRepository, 'save')

    def test_has_delete_method(self) -> None:
        assert hasattr(IDraftRepository, 'delete')

    def test_has_get_all_for_user_method(self) -> None:
        assert hasattr(IDraftRepository, 'get_all_for_user')


class TestISubmissionRepository:
    """Verify ISubmissionRepository protocol."""

    def test_has_get_by_id_method(self) -> None:
        assert hasattr(ISubmissionRepository, 'get_by_id')

    def test_has_save_method(self) -> None:
        assert hasattr(ISubmissionRepository, 'save')

    def test_has_get_for_problem_method(self) -> None:
        assert hasattr(ISubmissionRepository, 'get_for_problem')

    def test_has_get_for_user_method(self) -> None:
        assert hasattr(ISubmissionRepository, 'get_for_user')


class TestIProgressRepository:
    """Verify IProgressRepository protocol."""

    def test_has_get_method(self) -> None:
        assert hasattr(IProgressRepository, 'get')

    def test_has_save_method(self) -> None:
        assert hasattr(IProgressRepository, 'save')

    def test_has_get_all_for_user_method(self) -> None:
        assert hasattr(IProgressRepository, 'get_all_for_user')

    def test_has_get_solved_count_method(self) -> None:
        assert hasattr(IProgressRepository, 'get_solved_count')

    def test_has_get_solved_by_difficulty_method(self) -> None:
        assert hasattr(IProgressRepository, 'get_solved_by_difficulty')


class TestICodeExecutor:
    """Verify ICodeExecutor protocol."""

    def test_has_execute_method(self) -> None:
        assert hasattr(ICodeExecutor, 'execute')
        sig = inspect.signature(ICodeExecutor.execute)
        assert 'code' in sig.parameters
        assert 'test_cases' in sig.parameters
        assert 'function_name' in sig.parameters
        assert 'timeout_sec' in sig.parameters

    def test_has_validate_syntax_method(self) -> None:
        assert hasattr(ICodeExecutor, 'validate_syntax')


class TestIAuthProvider:
    """Verify IAuthProvider protocol."""

    def test_has_get_current_user_method(self) -> None:
        assert hasattr(IAuthProvider, 'get_current_user')

    def test_has_authenticate_method(self) -> None:
        assert hasattr(IAuthProvider, 'authenticate')


class TestAuthError:
    """Verify AuthError."""

    def test_is_domain_error_subclass(self) -> None:
        assert issubclass(AuthError, DomainError)

    def test_can_create(self) -> None:
        error = AuthError(message="Invalid token")
        assert error.message == "Invalid token"
