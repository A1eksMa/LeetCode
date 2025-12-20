# Step 9: Testing & CI

## Цель

Настроить полноценное тестирование проекта: unit-тесты, integration-тесты, Docker-окружение для тестов, CI pipeline.

## Принципы

- **TDD** — тесты для нового кода пишутся ДО или ВМЕСТЕ с кодом
- **Изоляция** — тесты запускаются в Docker для воспроизводимости
- **Coverage Gate** — минимум 80% покрытия, блокировка merge при падении
- **Fast Feedback** — unit-тесты быстрые (<5 сек), integration отдельно

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Общие fixtures
├── pytest.ini               # Конфигурация pytest
│
├── unit/                    # Быстрые, изолированные тесты
│   ├── __init__.py
│   ├── core/
│   │   ├── domain/
│   │   │   ├── test_result.py
│   │   │   ├── test_models.py
│   │   │   └── test_errors.py
│   │   ├── services/
│   │   │   ├── test_problems.py
│   │   │   ├── test_execution.py
│   │   │   ├── test_progress.py
│   │   │   └── test_drafts.py
│   │   └── ports/
│   │       └── test_protocols.py
│   │
│   ├── adapters/
│   │   ├── storage/
│   │   │   ├── test_json_problem_repository.py
│   │   │   ├── test_json_user_repository.py
│   │   │   └── test_json_draft_repository.py
│   │   ├── executors/
│   │   │   └── test_local_executor.py
│   │   └── auth/
│   │       └── test_anonymous_auth.py
│   │
│   ├── di/
│   │   ├── test_config.py
│   │   ├── test_container.py
│   │   └── test_providers.py
│   │
│   └── clients/
│       └── cli/
│           ├── test_app.py
│           ├── test_presenter.py
│           └── test_input_handler.py
│
├── integration/             # Тесты взаимодействия компонентов
│   ├── __init__.py
│   ├── test_solve_problem_flow.py
│   ├── test_progress_tracking.py
│   └── test_draft_persistence.py
│
├── e2e/                     # End-to-end тесты CLI
│   ├── __init__.py
│   └── test_cli_workflow.py
│
└── fixtures/                # Тестовые данные и фабрики
    ├── __init__.py
    ├── problems.py
    ├── users.py
    └── factories.py
```

## Задачи

### 9.1. Создать tests/conftest.py

```python
# tests/conftest.py
"""Shared pytest fixtures."""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from core.domain.models import (
    Problem,
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
    User,
)
from core.domain.enums import Difficulty, Language


# ============================================================
# Temporary Directories
# ============================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_data_dir(temp_dir):
    """Create data subdirectories."""
    (temp_dir / "problems").mkdir()
    (temp_dir / "users").mkdir()
    (temp_dir / "drafts").mkdir()
    (temp_dir / "submissions").mkdir()
    (temp_dir / "progress").mkdir()
    return temp_dir


# ============================================================
# Domain Model Fixtures
# ============================================================

@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id=1,
        title=LocalizedText({"en": "Two Sum", "ru": "Сумма двух чисел"}),
        description=LocalizedText({
            "en": "Given an array of integers nums and an integer target...",
            "ru": "Дан массив целых чисел nums и целое число target...",
        }),
        difficulty=Difficulty.EASY,
        tags=("array", "hash-table"),
        examples=(
            Example(
                input={"nums": [2, 7, 11, 15], "target": 9},
                output=[0, 1],
                explanation=LocalizedText({"en": "nums[0] + nums[1] = 9"}),
            ),
        ),
        test_cases=(
            TestCase(
                input={"nums": [2, 7, 11, 15], "target": 9},
                expected=[0, 1],
                description="basic case",
            ),
            TestCase(
                input={"nums": [3, 2, 4], "target": 6},
                expected=[1, 2],
                description="answer not at start",
            ),
        ),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def two_sum(nums: list[int], target: int) -> list[int]:",
                solutions=(
                    Solution(
                        name="Hash Map",
                        complexity="O(n)",
                        code="""def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []""",
                    ),
                ),
            ),
        ),
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="test_user_123",
        locale="en",
        preferred_language=Language.PYTHON,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def correct_solution_code():
    """Correct solution code for two_sum."""
    return """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []"""


@pytest.fixture
def wrong_solution_code():
    """Wrong solution code for two_sum."""
    return """def two_sum(nums, target):
    return [0, 0]"""


@pytest.fixture
def syntax_error_code():
    """Code with syntax error."""
    return """def two_sum(nums, target)
    return nums"""


# ============================================================
# Repository Fixtures
# ============================================================

@pytest.fixture
def problem_repo(temp_data_dir, sample_problem):
    """Create JsonProblemRepository with sample data."""
    import json
    from adapters.storage.json_problem_repository import JsonProblemRepository

    # Write sample problem to JSON
    problem_data = {
        "id": sample_problem.id,
        "title": sample_problem.title.translations,
        "description": sample_problem.description.translations,
        "difficulty": sample_problem.difficulty.value,
        "tags": list(sample_problem.tags),
        "examples": [
            {
                "input": ex.input,
                "output": ex.output,
                "explanation": ex.explanation.translations if ex.explanation else None,
            }
            for ex in sample_problem.examples
        ],
        "test_cases": [
            {
                "input": tc.input,
                "expected": tc.expected,
                "description": tc.description,
            }
            for tc in sample_problem.test_cases
        ],
        "languages": {
            "python3": {
                "function_signature": sample_problem.languages[0].function_signature,
                "solutions": [
                    {
                        "name": s.name,
                        "complexity": s.complexity,
                        "code": s.code,
                    }
                    for s in sample_problem.languages[0].solutions
                ],
            }
        },
    }

    problems_dir = temp_data_dir / "problems"
    (problems_dir / "1_two_sum.json").write_text(
        json.dumps(problem_data, ensure_ascii=False, indent=2)
    )

    return JsonProblemRepository(problems_dir)


@pytest.fixture
def user_repo(temp_data_dir):
    """Create JsonUserRepository."""
    from adapters.storage.json_user_repository import JsonUserRepository
    return JsonUserRepository(temp_data_dir / "users")


@pytest.fixture
def draft_repo(temp_data_dir):
    """Create JsonDraftRepository."""
    from adapters.storage.json_draft_repository import JsonDraftRepository
    return JsonDraftRepository(temp_data_dir / "drafts")


# ============================================================
# Executor Fixtures
# ============================================================

@pytest.fixture
def executor():
    """Create LocalExecutor for testing."""
    from adapters.executors.local_executor import LocalExecutor, ExecutorConfig
    return LocalExecutor(ExecutorConfig(timeout_sec=2))


# ============================================================
# Container Fixtures
# ============================================================

@pytest.fixture
def container(problem_repo, user_repo, draft_repo, executor):
    """Create a test container with all dependencies."""
    from unittest.mock import MagicMock
    from di.container import Container
    from adapters.auth.anonymous_auth import AnonymousAuthProvider

    return Container(
        problem_repo=problem_repo,
        user_repo=user_repo,
        draft_repo=draft_repo,
        submission_repo=MagicMock(),  # Not needed for most tests
        progress_repo=MagicMock(),    # Not needed for most tests
        executor=executor,
        auth=AnonymousAuthProvider("test_user"),
        default_locale="en",
        default_timeout_sec=2,
    )
```

### 9.2. Создать tests/fixtures/factories.py

```python
# tests/fixtures/factories.py
"""Factory functions for creating test data."""
from datetime import datetime
from uuid import uuid4

from core.domain.models import (
    Problem,
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
    User,
    Draft,
    Submission,
    Progress,
)
from core.domain.enums import Difficulty, Language, ProgressStatus


def create_problem(
    id: int = 1,
    title: str = "Test Problem",
    difficulty: Difficulty = Difficulty.EASY,
    tags: tuple[str, ...] = ("test",),
    with_solutions: bool = True,
) -> Problem:
    """Create a problem for testing."""
    solutions = ()
    if with_solutions:
        solutions = (
            Solution(
                name="Brute Force",
                complexity="O(n²)",
                code="def solution(x): return x",
            ),
        )

    return Problem(
        id=id,
        title=LocalizedText({"en": title}),
        description=LocalizedText({"en": f"Description for {title}"}),
        difficulty=difficulty,
        tags=tags,
        examples=(
            Example(
                input={"x": 1},
                output=2,
            ),
        ),
        test_cases=(
            TestCase(
                input={"x": 1},
                expected=2,
            ),
        ),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def solution(x: int) -> int:",
                solutions=solutions,
            ),
        ),
    )


def create_user(
    user_id: str | None = None,
    locale: str = "en",
    language: Language = Language.PYTHON,
) -> User:
    """Create a user for testing."""
    return User(
        id=user_id or f"user_{uuid4().hex[:8]}",
        locale=locale,
        preferred_language=language,
        created_at=datetime.now(),
    )


def create_draft(
    user_id: str = "test_user",
    problem_id: int = 1,
    code: str = "def solution(x): pass",
    language: Language = Language.PYTHON,
) -> Draft:
    """Create a draft for testing."""
    return Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )


def create_submission(
    user_id: str = "test_user",
    problem_id: int = 1,
    code: str = "def solution(x): return x * 2",
    execution_time_ms: int = 10,
) -> Submission:
    """Create a submission for testing."""
    return Submission(
        id=str(uuid4()),
        user_id=user_id,
        problem_id=problem_id,
        language=Language.PYTHON,
        code=code,
        execution_time_ms=execution_time_ms,
        memory_used_kb=1024,
        created_at=datetime.now(),
    )


def create_progress(
    user_id: str = "test_user",
    problem_id: int = 1,
    status: ProgressStatus = ProgressStatus.NOT_STARTED,
    attempts: int = 0,
) -> Progress:
    """Create progress for testing."""
    return Progress(
        user_id=user_id,
        problem_id=problem_id,
        status=status,
        attempts=attempts,
        solved_languages=(),
    )
```

### 9.3. Создать tests/integration/test_solve_problem_flow.py

```python
# tests/integration/test_solve_problem_flow.py
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
        sample_problem,
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
        assert "syntax" in result.error.message.lower()

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
        assert "ZeroDivision" in result.test_results[0].error_message
```

### 9.4. Создать Docker-конфигурацию для тестов

```dockerfile
# docker/Dockerfile.test
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Run tests with coverage
CMD ["pytest", \
     "--cov=core", \
     "--cov=adapters", \
     "--cov=di", \
     "--cov=clients", \
     "--cov-report=term-missing", \
     "--cov-report=html:htmlcov", \
     "--cov-fail-under=80", \
     "-v"]
```

```yaml
# docker/docker-compose.test.yml
version: '3.8'

services:
  test:
    build:
      context: ..
      dockerfile: docker/Dockerfile.test
    volumes:
      - ../htmlcov:/app/htmlcov
    environment:
      - PYTHONPATH=/app
      - CONFIG_PATH=/app/config/config.test.yaml

  test-watch:
    build:
      context: ..
      dockerfile: docker/Dockerfile.test
    volumes:
      - ..:/app
    command: ["pytest-watch", "--", "-v", "--tb=short"]
    environment:
      - PYTHONPATH=/app
```

### 9.5. Создать config/config.test.yaml

```yaml
# config/config.test.yaml
app:
  name: PracticeRaptor
  environment: testing
  default_locale: en

storage:
  type: json
  json:
    base_path: ./test_data

executor:
  type: local
  timeout_sec: 2
  memory_limit_mb: 128

auth:
  type: anonymous
```

### 9.6. Создать GitHub Actions CI

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run linters
        run: |
          ruff check .
          mypy core adapters di clients

      - name: Run tests
        run: |
          pytest \
            --cov=core \
            --cov=adapters \
            --cov=di \
            --cov=clients \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=80 \
            -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  test-docker:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run tests in Docker
        run: |
          docker-compose -f docker/docker-compose.test.yml up \
            --build \
            --abort-on-container-exit \
            --exit-code-from test
```

### 9.7. Обновить pyproject.toml для тестов

```toml
# Добавить в pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
addopts = "-v --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["core", "adapters", "di", "clients"]
branch = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
fail_under = 80
show_missing = true
```

## Команды для запуска тестов

```bash
# Локально
pytest                              # Все тесты
pytest tests/unit                   # Только unit
pytest tests/integration            # Только integration
pytest -v --tb=long                 # Verbose с полным traceback
pytest --cov --cov-report=html      # С coverage report

# В Docker
docker-compose -f docker/docker-compose.test.yml up --build

# Watch mode (для разработки)
docker-compose -f docker/docker-compose.test.yml run test-watch
```

## Критерии готовности

- [ ] Все тесты из Steps 1-8 проходят
- [ ] Coverage ≥ 80%
- [ ] mypy проходит без ошибок
- [ ] ruff check проходит
- [ ] Docker-окружение для тестов работает
- [ ] GitHub Actions CI настроен

## Чеклист тестового покрытия

### Core

- [ ] `core/domain/result.py` — Ok, Err, map, flat_map, unwrap
- [ ] `core/domain/models.py` — все модели, frozen, методы
- [ ] `core/domain/errors.py` — все типы ошибок
- [ ] `core/services/problems.py` — get, filter, random
- [ ] `core/services/execution.py` — validate, extract, run
- [ ] `core/services/progress.py` — get, update, stats
- [ ] `core/services/drafts.py` — get, save, delete

### Adapters

- [ ] `adapters/storage/json_*.py` — CRUD операции, edge cases
- [ ] `adapters/executors/local_executor.py` — success, error, timeout
- [ ] `adapters/auth/anonymous_auth.py` — get_current_user

### DI

- [ ] `di/config.py` — load, parse, defaults
- [ ] `di/providers.py` — create_container
- [ ] `di/container.py` — frozen, all fields

### Clients

- [ ] `clients/cli/app.py` — run modes, error handling
- [ ] `clients/cli/presenter.py` — formatting functions
- [ ] `clients/cli/input_handler.py` — user input, commands

## Завершение Stage 1.5

После завершения Step 9:

1. Все 9 шагов выполнены
2. CLI работает идентично прототипу
3. Тесты проходят с coverage ≥ 80%
4. mypy и ruff проходят
5. CI настроен и работает

Можно переходить к **Stage 1.6: CLI Enhancement**.
