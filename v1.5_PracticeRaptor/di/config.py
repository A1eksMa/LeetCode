"""Configuration loading and models."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class JsonStorageConfig:
    """JSON storage configuration."""
    base_path: Path = field(default_factory=lambda: Path("./data"))


@dataclass(frozen=True)
class SqliteStorageConfig:
    """SQLite storage configuration."""
    path: Path = field(default_factory=lambda: Path("./data/practiceraptor.db"))


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
