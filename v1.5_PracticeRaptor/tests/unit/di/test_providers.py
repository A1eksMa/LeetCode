"""Tests for DI providers."""
import pytest
import tempfile
from pathlib import Path

from di.config import (
    Config,
    AppConfig,
    StorageConfig,
    ExecutorConfig,
    AuthConfig,
    JsonStorageConfig,
)
from di.providers import create_container
from adapters.storage.json_problem_repository import JsonProblemRepository
from adapters.storage.json_user_repository import JsonUserRepository
from adapters.storage.json_draft_repository import JsonDraftRepository
from adapters.storage.json_submission_repository import JsonSubmissionRepository
from adapters.storage.json_progress_repository import JsonProgressRepository
from adapters.executors.local_executor import LocalExecutor
from adapters.auth.anonymous_auth import AnonymousAuthProvider


class TestCreateContainer:
    """Tests for create_container function."""

    def test_creates_json_container(self) -> None:
        """Create container with JSON storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
            )

            container = create_container(config)

            assert isinstance(container.problem_repo, JsonProblemRepository)
            assert isinstance(container.user_repo, JsonUserRepository)
            assert isinstance(container.draft_repo, JsonDraftRepository)
            assert isinstance(container.submission_repo, JsonSubmissionRepository)
            assert isinstance(container.progress_repo, JsonProgressRepository)

    def test_creates_local_executor(self) -> None:
        """Create container with local executor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
                executor=ExecutorConfig(type="local"),
            )

            container = create_container(config)

            assert isinstance(container.executor, LocalExecutor)

    def test_creates_anonymous_auth(self) -> None:
        """Create container with anonymous auth."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
                auth=AuthConfig(type="anonymous"),
            )

            container = create_container(config)

            assert isinstance(container.auth, AnonymousAuthProvider)

    def test_uses_config_locale(self) -> None:
        """Container uses locale from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                app=AppConfig(default_locale="ru"),
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
            )

            container = create_container(config)

            assert container.default_locale == "ru"

    def test_uses_config_timeout(self) -> None:
        """Container uses timeout from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
                executor=ExecutorConfig(timeout_sec=15),
            )

            container = create_container(config)

            assert container.default_timeout_sec == 15

    def test_raises_for_unknown_storage_type(self) -> None:
        """Raise error for unknown storage type."""
        config = Config(
            storage=StorageConfig(type="unknown"),
        )

        with pytest.raises(ValueError, match="Unknown storage type"):
            create_container(config)

    def test_raises_for_unknown_executor_type(self) -> None:
        """Raise error for unknown executor type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
                executor=ExecutorConfig(type="unknown"),
            )

            with pytest.raises(ValueError, match="Unknown executor type"):
                create_container(config)

    def test_raises_for_unknown_auth_type(self) -> None:
        """Raise error for unknown auth type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
                auth=AuthConfig(type="unknown"),
            )

            with pytest.raises(ValueError, match="Unknown auth type"):
                create_container(config)

    def test_sqlite_not_implemented(self) -> None:
        """SQLite storage raises NotImplementedError."""
        config = Config(
            storage=StorageConfig(type="sqlite"),
        )

        with pytest.raises(NotImplementedError, match="SQLite"):
            create_container(config)

    def test_postgresql_not_implemented(self) -> None:
        """PostgreSQL storage raises NotImplementedError."""
        config = Config(
            storage=StorageConfig(type="postgresql"),
        )

        with pytest.raises(NotImplementedError, match="PostgreSQL"):
            create_container(config)

    def test_docker_executor_not_implemented(self) -> None:
        """Docker executor raises NotImplementedError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                storage=StorageConfig(
                    type="json",
                    json=JsonStorageConfig(base_path=Path(tmpdir)),
                ),
                executor=ExecutorConfig(type="docker"),
            )

            with pytest.raises(NotImplementedError, match="Docker"):
                create_container(config)
