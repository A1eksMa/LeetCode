"""Ports layer - interfaces for external dependencies."""
from .repositories import (
    IProblemRepository,
    IUserRepository,
    IDraftRepository,
    ISubmissionRepository,
    IProgressRepository,
)
from .executors import ICodeExecutor
from .auth import IAuthProvider, AuthError

__all__ = [
    "IProblemRepository",
    "IUserRepository",
    "IDraftRepository",
    "ISubmissionRepository",
    "IProgressRepository",
    "ICodeExecutor",
    "IAuthProvider",
    "AuthError",
]
