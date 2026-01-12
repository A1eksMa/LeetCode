"""Dependency Injection container."""
from dataclasses import dataclass

from core.ports.repositories import (
    IProblemRepository,
    IUserRepository,
    IDraftRepository,
    ISubmissionRepository,
    IProgressRepository,
)
from core.ports.executors import ICodeExecutor
from core.ports.auth import IAuthProvider


@dataclass(frozen=True)
class Container:
    """
    Immutable container holding all application dependencies.

    Created once at application startup and passed to all components
    that need access to repositories, executor, or auth.
    """
    problem_repo: IProblemRepository
    user_repo: IUserRepository
    draft_repo: IDraftRepository
    submission_repo: ISubmissionRepository
    progress_repo: IProgressRepository
    executor: ICodeExecutor
    auth: IAuthProvider

    # Configuration
    default_locale: str = "en"
    default_timeout_sec: int = 5
