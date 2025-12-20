# Step 7: DI Container

## Цель

Создать систему Dependency Injection для сборки приложения из компонентов на основе конфигурации.

## Принципы

- **Ручная реализация** — без библиотек (python-dependency-injector и т.п.)
- **Container как frozen dataclass** — неизменяемый контейнер зависимостей
- **Factory functions** — создание зависимостей на основе конфигурации
- **Конфигурация через YAML** — переключение адаптеров без изменения кода

## Задачи

### 7.1. Создать di/config.py

```python
# di/config.py
"""Configuration loading and models."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class JsonStorageConfig:
    """JSON storage configuration."""
    base_path: Path = Path("./data")


@dataclass(frozen=True)
class SqliteStorageConfig:
    """SQLite storage configuration."""
    path: Path = Path("./data/practiceraptor.db")


@dataclass(frozen=True)
class PostgresStorageConfig:
    """PostgreSQL storage configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "practiceraptor"
    user: str = ""
    password: str = ""


@dataclass(frozen=True)
class StorageConfig:
    """Storage configuration."""
    type: str = "json"  # json | sqlite | postgresql
    json: JsonStorageConfig = field(default_factory=JsonStorageConfig)
    sqlite: SqliteStorageConfig = field(default_factory=SqliteStorageConfig)
    postgresql: PostgresStorageConfig = field(default_factory=PostgresStorageConfig)


@dataclass(frozen=True)
class ExecutorConfig:
    """Executor configuration."""
    type: str = "local"  # local | docker | remote
    timeout_sec: int = 5
    memory_limit_mb: int = 256


@dataclass(frozen=True)
class AuthConfig:
    """Authentication configuration."""
    type: str = "anonymous"  # anonymous | telegram | token


@dataclass(frozen=True)
class AppConfig:
    """Application configuration."""
    name: str = "PracticeRaptor"
    environment: str = "development"
    default_locale: str = "en"


@dataclass(frozen=True)
class Config:
    """Root configuration."""
    app: AppConfig = field(default_factory=AppConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    executor: ExecutorConfig = field(default_factory=ExecutorConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)


def load_config(config_path: Path | None = None) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, uses defaults.

    Returns:
        Config object with loaded or default values.
    """
    if config_path is None or not config_path.exists():
        return Config()

    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    return _parse_config(data)


def _parse_config(data: dict[str, Any]) -> Config:
    """Parse configuration dictionary into Config object."""
    app_data = data.get("app", {})
    app = AppConfig(
        name=app_data.get("name", "PracticeRaptor"),
        environment=app_data.get("environment", "development"),
        default_locale=app_data.get("default_locale", "en"),
    )

    storage_data = data.get("storage", {})
    json_data = storage_data.get("json", {})
    sqlite_data = storage_data.get("sqlite", {})
    pg_data = storage_data.get("postgresql", {})

    storage = StorageConfig(
        type=storage_data.get("type", "json"),
        json=JsonStorageConfig(
            base_path=Path(json_data.get("base_path", "./data")),
        ),
        sqlite=SqliteStorageConfig(
            path=Path(sqlite_data.get("path", "./data/practiceraptor.db")),
        ),
        postgresql=PostgresStorageConfig(
            host=pg_data.get("host", "localhost"),
            port=pg_data.get("port", 5432),
            database=pg_data.get("database", "practiceraptor"),
            user=pg_data.get("user", ""),
            password=pg_data.get("password", ""),
        ),
    )

    executor_data = data.get("executor", {})
    executor = ExecutorConfig(
        type=executor_data.get("type", "local"),
        timeout_sec=executor_data.get("timeout_sec", 5),
        memory_limit_mb=executor_data.get("memory_limit_mb", 256),
    )

    auth_data = data.get("auth", {})
    auth = AuthConfig(
        type=auth_data.get("type", "anonymous"),
    )

    return Config(
        app=app,
        storage=storage,
        executor=executor,
        auth=auth,
    )
```

### 7.2. Создать di/container.py

```python
# di/container.py
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
```

### 7.3. Создать di/providers.py

```python
# di/providers.py
"""Factory functions for creating dependencies."""
from pathlib import Path

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
            from adapters.executors.local_executor import LocalExecutor, ExecutorConfig as ExecConfig
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
```

### 7.4. Создать adapters/auth/anonymous_auth.py

```python
# adapters/auth/anonymous_auth.py
"""Anonymous authentication provider for CLI."""
from datetime import datetime
from uuid import uuid4

from core.domain.models import User
from core.domain.enums import Language
from core.domain.result import Ok, Result
from core.ports.auth import IAuthProvider, AuthError


class AnonymousAuthProvider:
    """
    Authentication provider for anonymous/local users.

    Used in CLI mode where no real authentication is needed.
    Creates a local user with a persistent ID stored in config.
    """

    def __init__(self, user_id: str | None = None):
        """
        Initialize with optional fixed user ID.

        Args:
            user_id: Fixed user ID. If None, generates a new one.
        """
        self._user_id = user_id or f"local_{uuid4().hex[:8]}"
        self._user: User | None = None

    def get_current_user(self) -> Result[User, AuthError]:
        """Get the local anonymous user."""
        if self._user is None:
            self._user = User(
                id=self._user_id,
                locale="en",
                preferred_language=Language.PYTHON,
                created_at=datetime.now(),
            )
        return Ok(self._user)

    def authenticate(self, credentials: dict) -> Result[User, AuthError]:
        """
        Authenticate with credentials.

        For anonymous auth, this just returns the current user.
        Credentials are ignored.
        """
        return self.get_current_user()
```

### 7.5. Обновить di/__init__.py

```python
# di/__init__.py
"""Dependency Injection module."""
from .config import Config, load_config
from .container import Container
from .providers import create_container

__all__ = [
    "Config",
    "load_config",
    "Container",
    "create_container",
]
```

### 7.6. Обновить adapters/auth/__init__.py

```python
# adapters/auth/__init__.py
"""Authentication adapters."""
from .anonymous_auth import AnonymousAuthProvider

__all__ = [
    "AnonymousAuthProvider",
]
```

## Использование

```python
# В точке входа приложения (main.py)
from pathlib import Path
from di import load_config, create_container

# Загрузка конфигурации
config = load_config(Path("config/config.yaml"))

# Создание контейнера
container = create_container(config)

# Использование зависимостей
problems = container.problem_repo.get_all()
user = container.auth.get_current_user()
```

## Диаграмма зависимостей

```
                    ┌─────────────────┐
                    │   config.yaml   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  load_config()  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Config      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │create_container()│
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │ Storage  │       │ Executor │       │   Auth   │
    │ Adapters │       │ Adapter  │       │ Adapter  │
    └────┬─────┘       └────┬─────┘       └────┬─────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │    Container    │
                    │  (frozen DC)    │
                    └─────────────────┘
```

## Критерии готовности

- [ ] Config загружается из YAML
- [ ] Container — frozen dataclass
- [ ] Все providers реализованы для JSON storage
- [ ] AnonymousAuthProvider работает
- [ ] Тесты для config и container
- [ ] mypy проходит

## Тесты для Step 7

```python
# tests/unit/di/test_config.py
import pytest
import tempfile
from pathlib import Path

from di.config import load_config, Config


class TestLoadConfig:
    def test_returns_defaults_when_no_file(self):
        config = load_config(None)

        assert config.app.name == "PracticeRaptor"
        assert config.storage.type == "json"
        assert config.executor.type == "local"
        assert config.auth.type == "anonymous"

    def test_loads_from_yaml(self):
        yaml_content = """
app:
  name: TestApp
  environment: testing

storage:
  type: json
  json:
    base_path: ./test_data

executor:
  type: local
  timeout_sec: 10
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()

            config = load_config(Path(f.name))

            assert config.app.name == "TestApp"
            assert config.executor.timeout_sec == 10


# tests/unit/di/test_container.py
import pytest
from di.container import Container
from unittest.mock import MagicMock


class TestContainer:
    def test_is_frozen(self):
        container = Container(
            problem_repo=MagicMock(),
            user_repo=MagicMock(),
            draft_repo=MagicMock(),
            submission_repo=MagicMock(),
            progress_repo=MagicMock(),
            executor=MagicMock(),
            auth=MagicMock(),
        )

        with pytest.raises(AttributeError):
            container.problem_repo = MagicMock()


# tests/unit/di/test_providers.py
import pytest
import tempfile
from pathlib import Path

from di.config import Config
from di.providers import create_container


class TestCreateContainer:
    def test_creates_json_container(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config()
            config = Config(
                storage=config.storage.__class__(
                    type="json",
                    json=config.storage.json.__class__(
                        base_path=Path(tmpdir),
                    ),
                ),
            )

            container = create_container(config)

            assert container.problem_repo is not None
            assert container.executor is not None
            assert container.auth is not None
```

## Следующий шаг

После завершения Step 7 переходите к [Step 8: CLI Refactoring](./08_cli_refactoring.md).
