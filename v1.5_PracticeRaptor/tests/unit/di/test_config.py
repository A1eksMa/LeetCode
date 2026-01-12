"""Tests for DI configuration."""
import pytest
import tempfile
from pathlib import Path

from di.config import (
    load_config,
    Config,
    AppConfig,
    StorageConfig,
    ExecutorConfig,
    AuthConfig,
    JsonStorageConfig,
)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_returns_defaults_when_no_file(self) -> None:
        """Return default config when no file specified."""
        config = load_config(None)

        assert config.app.name == "PracticeRaptor"
        assert config.storage.type == "json"
        assert config.executor.type == "local"
        assert config.auth.type == "anonymous"

    def test_returns_defaults_for_nonexistent_file(self) -> None:
        """Return default config when file doesn't exist."""
        config = load_config(Path("/nonexistent/config.yaml"))

        assert config.app.name == "PracticeRaptor"
        assert config.storage.type == "json"

    def test_loads_from_yaml(self) -> None:
        """Load config from YAML file."""
        yaml_content = """
app:
  name: TestApp
  environment: testing
  default_locale: ru

storage:
  type: json
  json:
    base_path: ./test_data

executor:
  type: local
  timeout_sec: 10
  memory_limit_mb: 512

auth:
  type: anonymous
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()
            path = Path(f.name)

        try:
            config = load_config(path)

            assert config.app.name == "TestApp"
            assert config.app.environment == "testing"
            assert config.app.default_locale == "ru"
            assert config.storage.type == "json"
            assert config.storage.json.base_path == Path("./test_data")
            assert config.executor.timeout_sec == 10
            assert config.executor.memory_limit_mb == 512
        finally:
            path.unlink()

    def test_partial_yaml_uses_defaults(self) -> None:
        """Partial YAML file uses defaults for missing values."""
        yaml_content = """
app:
  name: PartialApp
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()
            path = Path(f.name)

        try:
            config = load_config(path)

            assert config.app.name == "PartialApp"
            assert config.app.environment == "development"
            assert config.storage.type == "json"
            assert config.executor.timeout_sec == 5
        finally:
            path.unlink()

    def test_empty_yaml_uses_defaults(self) -> None:
        """Empty YAML file uses all defaults."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            config = load_config(path)

            assert config.app.name == "PracticeRaptor"
            assert config.storage.type == "json"
        finally:
            path.unlink()

    def test_loads_postgresql_config(self) -> None:
        """Load PostgreSQL configuration."""
        yaml_content = """
storage:
  type: postgresql
  postgresql:
    host: db.example.com
    port: 5433
    database: practice_db
    user: admin
    password: secret
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()
            path = Path(f.name)

        try:
            config = load_config(path)

            assert config.storage.type == "postgresql"
            assert config.storage.postgresql.host == "db.example.com"
            assert config.storage.postgresql.port == 5433
            assert config.storage.postgresql.database == "practice_db"
            assert config.storage.postgresql.user == "admin"
            assert config.storage.postgresql.password == "secret"
        finally:
            path.unlink()


class TestConfigImmutability:
    """Tests for config immutability."""

    def test_config_is_frozen(self) -> None:
        """Config should be immutable."""
        config = Config()

        with pytest.raises(AttributeError):
            config.app = AppConfig(name="Changed")

    def test_app_config_is_frozen(self) -> None:
        """AppConfig should be immutable."""
        config = AppConfig()

        with pytest.raises(AttributeError):
            config.name = "Changed"

    def test_storage_config_is_frozen(self) -> None:
        """StorageConfig should be immutable."""
        config = StorageConfig()

        with pytest.raises(AttributeError):
            config.type = "sqlite"

    def test_executor_config_is_frozen(self) -> None:
        """ExecutorConfig should be immutable."""
        config = ExecutorConfig()

        with pytest.raises(AttributeError):
            config.timeout_sec = 100


class TestConfigDefaults:
    """Tests for config default values."""

    def test_app_defaults(self) -> None:
        """AppConfig has correct defaults."""
        config = AppConfig()

        assert config.name == "PracticeRaptor"
        assert config.environment == "development"
        assert config.default_locale == "en"

    def test_storage_defaults(self) -> None:
        """StorageConfig has correct defaults."""
        config = StorageConfig()

        assert config.type == "json"
        assert config.json.base_path == Path("./data")

    def test_executor_defaults(self) -> None:
        """ExecutorConfig has correct defaults."""
        config = ExecutorConfig()

        assert config.type == "local"
        assert config.timeout_sec == 5
        assert config.memory_limit_mb == 256

    def test_auth_defaults(self) -> None:
        """AuthConfig has correct defaults."""
        config = AuthConfig()

        assert config.type == "anonymous"
