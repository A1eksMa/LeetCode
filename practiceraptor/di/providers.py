"""Factory functions for creating dependencies."""
from .config import Config, StorageConfig, ExecutorConfig, AuthConfig
from .container import Container

from core.ports.repositories import (
    IProblemRepository,
    IUserRepository,
    IDraftRepository,
    ISubmissionRepository,
    IProgressRepository,
)
from core.ports.executors import ICodeExecutor
from core.ports.auth import IAuthProvider


def create_container(config: Config) -> Container:
    """
    Create dependency container from configuration.

    This is the main factory function that assembles all
    dependencies based on the provided configuration.

    Args:
        config: Application configuration

    Returns:
        Fully initialized Container with all dependencies
    """
    # Create repositories
    problem_repo = _create_problem_repo(config.storage)
    user_repo = _create_user_repo(config.storage)
    draft_repo = _create_draft_repo(config.storage)
    submission_repo = _create_submission_repo(config.storage)
    progress_repo = _create_progress_repo(config.storage)

    # Create executor
    executor = _create_executor(config.executor)

    # Create auth provider
    auth = _create_auth(config.auth)

    return Container(
        problem_repo=problem_repo,
        user_repo=user_repo,
        draft_repo=draft_repo,
        submission_repo=submission_repo,
        progress_repo=progress_repo,
        executor=executor,
        auth=auth,
        default_locale=config.app.default_locale,
        default_timeout_sec=config.executor.timeout_sec,
    )


# ============================================================
# Repository Providers
# ============================================================

def _create_problem_repo(config: StorageConfig) -> IProblemRepository:
    """Create problem repository based on storage type."""
    match config.type:
        case "json":
            from adapters.storage.json_problem_repository import JsonProblemRepository
            return JsonProblemRepository(config.json.base_path / "problems")
        case "sqlite":
            raise NotImplementedError("SQLite storage not yet implemented")
        case "postgresql":
            raise NotImplementedError("PostgreSQL storage not yet implemented")
        case _:
            raise ValueError(f"Unknown storage type: {config.type}")


def _create_user_repo(config: StorageConfig) -> IUserRepository:
    """Create user repository based on storage type."""
    match config.type:
        case "json":
            from adapters.storage.json_user_repository import JsonUserRepository
            return JsonUserRepository(config.json.base_path / "users")
        case "sqlite":
            raise NotImplementedError("SQLite storage not yet implemented")
        case "postgresql":
            raise NotImplementedError("PostgreSQL storage not yet implemented")
        case _:
            raise ValueError(f"Unknown storage type: {config.type}")


def _create_draft_repo(config: StorageConfig) -> IDraftRepository:
    """Create draft repository based on storage type."""
    match config.type:
        case "json":
            from adapters.storage.json_draft_repository import JsonDraftRepository
            return JsonDraftRepository(config.json.base_path / "drafts")
        case "sqlite":
            raise NotImplementedError("SQLite storage not yet implemented")
        case "postgresql":
            raise NotImplementedError("PostgreSQL storage not yet implemented")
        case _:
            raise ValueError(f"Unknown storage type: {config.type}")


def _create_submission_repo(config: StorageConfig) -> ISubmissionRepository:
    """Create submission repository based on storage type."""
    match config.type:
        case "json":
            from adapters.storage.json_submission_repository import JsonSubmissionRepository
            return JsonSubmissionRepository(config.json.base_path / "submissions")
        case "sqlite":
            raise NotImplementedError("SQLite storage not yet implemented")
        case "postgresql":
            raise NotImplementedError("PostgreSQL storage not yet implemented")
        case _:
            raise ValueError(f"Unknown storage type: {config.type}")


def _create_progress_repo(config: StorageConfig) -> IProgressRepository:
    """Create progress repository based on storage type."""
    match config.type:
        case "json":
            from adapters.storage.json_progress_repository import JsonProgressRepository
            return JsonProgressRepository(config.json.base_path / "progress")
        case "sqlite":
            raise NotImplementedError("SQLite storage not yet implemented")
        case "postgresql":
            raise NotImplementedError("PostgreSQL storage not yet implemented")
        case _:
            raise ValueError(f"Unknown storage type: {config.type}")


# ============================================================
# Executor Providers
# ============================================================

def _create_executor(config: ExecutorConfig) -> ICodeExecutor:
    """Create code executor based on type."""
    match config.type:
        case "local":
            from adapters.executors.local_executor import (
                LocalExecutor,
                ExecutorConfig as ExecConfig,
            )
            return LocalExecutor(ExecConfig(
                timeout_sec=config.timeout_sec,
                memory_limit_mb=config.memory_limit_mb,
            ))
        case "docker":
            raise NotImplementedError("Docker executor not yet implemented")
        case "remote":
            raise NotImplementedError("Remote executor not yet implemented")
        case _:
            raise ValueError(f"Unknown executor type: {config.type}")


# ============================================================
# Auth Providers
# ============================================================

def _create_auth(config: AuthConfig) -> IAuthProvider:
    """Create auth provider based on type."""
    match config.type:
        case "anonymous":
            from adapters.auth.anonymous_auth import AnonymousAuthProvider
            return AnonymousAuthProvider()
        case "telegram":
            raise NotImplementedError("Telegram auth not yet implemented")
        case "token":
            raise NotImplementedError("Token auth not yet implemented")
        case _:
            raise ValueError(f"Unknown auth type: {config.type}")
