"""Executor adapters for code execution."""
from .local_executor import LocalExecutor, ExecutorConfig

__all__ = [
    "LocalExecutor",
    "ExecutorConfig",
]
