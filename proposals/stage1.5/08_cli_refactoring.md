# Step 8: CLI Refactoring

## Цель

Рефакторинг текущего CLI-прототипа для использования ядра через DI Container. CLI должен работать **идентично** текущему, но через абстракции.

## Принципы

- **Тонкий клиент** — CLI отвечает только за UI (ввод/вывод)
- **Вся логика в core** — бизнес-логика вызывается через сервисы
- **Зависимости через Container** — все репозитории и executor из DI
- **Обратная совместимость** — пользовательский опыт не меняется

## Структура clients/cli/

```
clients/cli/
├── __init__.py
├── main.py              # Точка входа, парсинг аргументов
├── app.py               # Главный класс приложения
├── presenter.py         # Форматирование вывода
├── input_handler.py     # Обработка пользовательского ввода
├── colors.py            # ANSI colors (из config.py)
└── commands/            # Команды (опционально для будущего)
    └── __init__.py
```

## Задачи

### 8.1. Создать clients/cli/colors.py

```python
# clients/cli/colors.py
"""ANSI color codes for terminal output."""


class Colors:
    """ANSI escape codes for colored output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @classmethod
    def success(cls, text: str) -> str:
        """Green text for success."""
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def error(cls, text: str) -> str:
        """Red text for errors."""
        return f"{cls.RED}{text}{cls.RESET}"

    @classmethod
    def warning(cls, text: str) -> str:
        """Yellow text for warnings."""
        return f"{cls.YELLOW}{text}{cls.RESET}"

    @classmethod
    def info(cls, text: str) -> str:
        """Cyan text for info."""
        return f"{cls.CYAN}{text}{cls.RESET}"

    @classmethod
    def muted(cls, text: str) -> str:
        """Gray text for secondary info."""
        return f"{cls.GRAY}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Bold text."""
        return f"{cls.BOLD}{text}{cls.RESET}"


# Separators
SEPARATOR = "─" * 40
DOUBLE_SEPARATOR = "═" * 40
```

### 8.2. Создать clients/cli/presenter.py

```python
# clients/cli/presenter.py
"""Output formatting for CLI."""
from core.domain.models import Problem, ExecutionResult, TestResult
from core.domain.enums import Difficulty
from core.services import get_problem_display_text, format_examples

from .colors import Colors, SEPARATOR, DOUBLE_SEPARATOR


def display_welcome() -> None:
    """Display welcome banner."""
    banner = f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║       PracticeRaptor CLI               ║
╚════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def display_problem_list(problems: tuple, locale: str = "en") -> None:
    """Display list of available problems."""
    print("\nAvailable problems:")
    print(f"  [{Colors.info('0')}] Random problem")

    for i, problem in enumerate(problems, 1):
        diff_color = _get_difficulty_color(problem.difficulty)
        diff_str = f"{diff_color}{problem.difficulty.value}{Colors.RESET}"
        tags_str = ", ".join(problem.tags)
        title = problem.title.get(locale)

        print(f"  [{i}] {title} ({diff_str}) [{tags_str}]")

    print()


def display_problem(problem: Problem, language: str, locale: str = "en") -> None:
    """Display full problem description."""
    # Header
    print(SEPARATOR)
    print(f"Problem #{problem.id}: {Colors.bold(problem.title.get(locale))}")

    diff_color = _get_difficulty_color(problem.difficulty)
    print(f"Difficulty: {diff_color}{problem.difficulty.value}{Colors.RESET}")
    print(f"Tags: {', '.join(problem.tags)}")
    print(SEPARATOR)

    # Description
    print()
    print(problem.description.get(locale))

    # Examples
    examples = format_examples(problem, locale)
    for ex in examples:
        print(f"\n{Colors.bold(f'Example {ex[\"number\"]}:')}")
        print(f"  Input: {_format_input(ex['input'])}")
        print(f"  Output: {ex['output']}")
        if "explanation" in ex:
            print(f"  {Colors.muted('Explanation: ' + ex['explanation'])}")

    # Function signature
    lang_spec = problem.get_language_spec(language)
    if lang_spec:
        print(f"\n{Colors.bold('Function signature:')}")
        print(f"  {Colors.info(lang_spec.function_signature)}")

    print()
    print(SEPARATOR)


def display_results(result: ExecutionResult, verbose: bool = False) -> None:
    """Display test execution results."""
    print("\nRunning tests...\n")

    for test_result in result.test_results:
        _display_test_result(test_result, verbose)

        if not test_result.passed:
            _display_error_details(test_result)
            print()

    # Summary
    print(DOUBLE_SEPARATOR)
    if result.success:
        print(Colors.success("✓ All tests passed!"))
    else:
        print(Colors.error(f"✗ Tests failed: {result.passed_count}/{result.total_count}"))

    print(f"  Execution time: {result.total_time_ms}ms")
    print(DOUBLE_SEPARATOR)


def display_hint(solution_name: str, complexity: str, code: str, index: int, total: int) -> None:
    """Display a canonical solution as hint."""
    print(f"\n{Colors.warning('═' * 40)}")
    print(Colors.warning(f"Hint {index}/{total}: {solution_name}"))
    print(Colors.muted(f"Complexity: {complexity}"))
    print(Colors.warning('─' * 40))
    print(Colors.info(code))
    print(Colors.warning('═' * 40))
    print()


def display_message(message: str, style: str = "info") -> None:
    """Display a styled message."""
    match style:
        case "success":
            print(Colors.success(message))
        case "error":
            print(Colors.error(message))
        case "warning":
            print(Colors.warning(message))
        case _:
            print(Colors.info(message))


def _get_difficulty_color(difficulty: Difficulty) -> str:
    """Get color for difficulty level."""
    match difficulty:
        case Difficulty.EASY:
            return Colors.GREEN
        case Difficulty.MEDIUM:
            return Colors.YELLOW
        case Difficulty.HARD:
            return Colors.RED


def _format_input(input_data: dict) -> str:
    """Format input data for display."""
    parts = [f"{k} = {v}" for k, v in input_data.items()]
    return ", ".join(parts)


def _display_test_result(result: TestResult, verbose: bool) -> None:
    """Display single test result line."""
    time_str = f"({result.execution_time_ms}ms)"

    if result.passed:
        status_icon = Colors.success("✓")
        status_text = "passed"
    else:
        status_icon = Colors.error("✗")
        status_text = "failed" if result.error_message and "Expected" in result.error_message else "error"

    desc = result.test_case.description or ""
    line = f"{status_icon} Test: {status_text} {time_str}"

    if verbose and desc:
        line += f" - {Colors.muted(desc)}"

    print(line)


def _display_error_details(result: TestResult) -> None:
    """Display details for failed test."""
    if result.test_case.description:
        print(f"  {Colors.muted(f'Test: {result.test_case.description}')}")

    if result.error_message:
        if "Expected" in result.error_message:
            # Wrong answer
            print(f"  Input: {Colors.info(str(result.test_case.input))}")
            print(f"  Expected: {Colors.success(str(result.test_case.expected))}")
            print(f"  Actual: {Colors.error(str(result.actual))}")
        else:
            # Runtime error
            print(f"  {Colors.error(f'Error: {result.error_message}')}")
```

### 8.3. Создать clients/cli/input_handler.py

```python
# clients/cli/input_handler.py
"""User input handling for CLI."""
from dataclasses import dataclass

from core.domain.models import Problem
from core.domain.enums import Language

from .colors import Colors
from .presenter import display_hint


@dataclass
class InputResult:
    """Result of user code input."""
    code: str | None = None
    cancelled: bool = False


def get_user_choice(min_val: int, max_val: int, prompt: str = "Choose") -> int:
    """Get numeric choice from user."""
    while True:
        try:
            user_input = input(f"{prompt} ({min_val}-{max_val}): ").strip()
            value = int(user_input)

            if min_val <= value <= max_val:
                return value
            else:
                print(Colors.error(f"Enter a number from {min_val} to {max_val}"))
        except ValueError:
            print(Colors.error("Enter a number"))


def read_user_code(
    problem: Problem,
    language: Language,
    previous_code: str | None = None,
) -> InputResult:
    """
    Read multiline code from user.

    Supports commands:
    - !hint: Show canonical solution
    - !reset: Clear entered code
    - !cancel: Cancel and return to menu

    Input ends with double Enter (two empty lines).
    """
    hint_index = 0
    lang_spec = problem.get_language_spec(language)
    solutions = lang_spec.solutions if lang_spec else ()

    # Show previous code if any
    if previous_code:
        _show_previous_code(previous_code)

    print("Enter your solution (double Enter to submit, !hint for help):")

    lines: list[str] = []
    empty_count = 0

    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break

        # Check commands
        stripped = line.strip().lower()

        if stripped == "!hint":
            if solutions and hint_index < len(solutions):
                sol = solutions[hint_index]
                display_hint(sol.name, sol.complexity, sol.code, hint_index + 1, len(solutions))
                hint_index += 1
            elif not solutions:
                print(Colors.warning("\nNo hints available for this problem.\n"))
            else:
                print(Colors.warning("\nNo more hints.\n"))
            continue

        if stripped == "!reset":
            lines = []
            empty_count = 0
            print(Colors.info("Code cleared. Enter again:"))
            continue

        if stripped == "!cancel":
            return InputResult(cancelled=True)

        # Handle empty lines
        if not line.strip():
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append("")
        else:
            empty_count = 0
            lines.append(line)

    # Remove trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    code = "\n".join(lines)

    if not code.strip():
        return InputResult(cancelled=True)

    return InputResult(code=code)


def read_code_from_file(file_path: str) -> str:
    """Read code from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def ask_continue() -> bool:
    """Ask user if they want to continue."""
    while True:
        answer = input("\nContinue? (y/n): ").strip().lower()
        if answer in ("y", "yes", ""):
            return True
        if answer in ("n", "no"):
            return False
        print("Enter y or n")


def ask_retry() -> bool:
    """Ask user if they want to retry."""
    answer = input("\nTry again? (y/n): ").strip().lower()
    return answer in ("y", "yes", "")


def _show_previous_code(code: str) -> None:
    """Display previous code for reference."""
    print(Colors.muted("\nPrevious code:"))
    print(Colors.muted("┌" + "─" * 38))
    for line in code.split("\n"):
        print(Colors.muted(f"│ {line}"))
    print(Colors.muted("└" + "─" * 38))
    print()
```

### 8.4. Создать clients/cli/app.py

```python
# clients/cli/app.py
"""Main CLI application class."""
import random

from core.domain.models import Problem
from core.domain.enums import Language
from core.domain.result import Ok, Err
from core.services import (
    get_all_problems,
    get_problem,
    validate_code_syntax,
    run_full_tests,
)
from di import Container

from .presenter import (
    display_welcome,
    display_problem_list,
    display_problem,
    display_results,
    display_message,
)
from .input_handler import (
    get_user_choice,
    read_user_code,
    read_code_from_file,
    ask_continue,
    ask_retry,
    InputResult,
)


class CLIApp:
    """
    Main CLI application.

    Orchestrates the problem-solving flow using core services
    and dependencies from the DI container.
    """

    def __init__(self, container: Container):
        self.container = container
        self.locale = container.default_locale
        self.language = Language.PYTHON

    def run(self, task_id: int | None = None, file_path: str | None = None, verbose: bool = False) -> int:
        """
        Run the CLI application.

        Args:
            task_id: Optional problem ID to jump to
            file_path: Optional file with solution code
            verbose: Show verbose output

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        # Load problems
        problems = get_all_problems(self.container.problem_repo)

        if not problems:
            display_message("No problems found", "error")
            return 1

        display_welcome()

        # Handle file mode
        if file_path:
            return self._run_file_mode(problems, task_id, file_path, verbose)

        # Handle direct task mode
        if task_id:
            return self._run_single_task(problems, task_id, verbose)

        # Interactive mode
        return self._run_interactive(problems, verbose)

    def _run_file_mode(
        self,
        problems: tuple[Problem, ...],
        task_id: int | None,
        file_path: str,
        verbose: bool,
    ) -> int:
        """Run with code from file."""
        try:
            code = read_code_from_file(file_path)
        except FileNotFoundError:
            display_message(f"File not found: {file_path}", "error")
            return 1

        if task_id:
            problem = self._get_problem_by_index(problems, task_id)
            if not problem:
                display_message(f"Problem #{task_id} not found", "error")
                return 1
        else:
            problem = self._select_problem(problems)

        return self._solve_with_code(problem, code, verbose)

    def _run_single_task(
        self,
        problems: tuple[Problem, ...],
        task_id: int,
        verbose: bool,
    ) -> int:
        """Run single task by ID."""
        problem = self._get_problem_by_index(problems, task_id)
        if not problem:
            display_message(f"Problem #{task_id} not found", "error")
            return 1

        success = self._solve_problem(problem, verbose)
        return 0 if success else 1

    def _run_interactive(self, problems: tuple[Problem, ...], verbose: bool) -> int:
        """Run interactive mode."""
        while True:
            try:
                problem = self._select_problem(problems)
                self._solve_problem(problem, verbose)

                if not ask_continue():
                    break

            except KeyboardInterrupt:
                print("\n")
                break

        display_message("\nGoodbye!", "info")
        return 0

    def _select_problem(self, problems: tuple[Problem, ...]) -> Problem:
        """Display problem list and get user selection."""
        display_problem_list(problems, self.locale)

        choice = get_user_choice(0, len(problems))

        if choice == 0:
            problem = random.choice(problems)
            display_message(f"\nRandom problem: {problem.title.get(self.locale)}", "info")
            return problem

        return problems[choice - 1]

    def _get_problem_by_index(self, problems: tuple[Problem, ...], index: int) -> Problem | None:
        """Get problem by 1-based index."""
        if 1 <= index <= len(problems):
            return problems[index - 1]
        return None

    def _solve_problem(self, problem: Problem, verbose: bool) -> bool:
        """
        Full problem solving flow.

        Returns True if solved successfully.
        """
        display_problem(problem, self.language.value, self.locale)

        previous_code = None

        while True:
            # Get code from user
            result = read_user_code(problem, self.language, previous_code)

            if result.cancelled:
                display_message("\nCancelled.", "warning")
                return False

            code = result.code

            # Validate syntax
            syntax_result = validate_code_syntax(code)
            if syntax_result.is_err():
                display_message(f"\n✗ Syntax error: {syntax_result.error.message}", "error")
                display_message("Try again.", "warning")
                previous_code = code
                continue

            # Run tests
            success = self._run_and_display_results(problem, code, verbose)

            if success:
                return True

            # Ask to retry
            if not ask_retry():
                return False

            previous_code = code

    def _solve_with_code(self, problem: Problem, code: str, verbose: bool) -> int:
        """Solve with provided code (file mode)."""
        display_problem(problem, self.language.value, self.locale)

        # Validate syntax
        syntax_result = validate_code_syntax(code)
        if syntax_result.is_err():
            display_message(f"\n✗ Syntax error: {syntax_result.error.message}", "error")
            return 1

        success = self._run_and_display_results(problem, code, verbose)
        return 0 if success else 1

    def _run_and_display_results(self, problem: Problem, code: str, verbose: bool) -> bool:
        """Run tests and display results."""
        result = run_full_tests(
            code=code,
            problem=problem,
            language=self.language,
            executor=self.container.executor,
        )

        match result:
            case Ok(exec_result):
                display_results(exec_result, verbose)
                return exec_result.success
            case Err(error):
                display_message(f"\n✗ Execution error: {error.message}", "error")
                return False
```

### 8.5. Создать clients/cli/main.py

```python
# clients/cli/main.py
#!/usr/bin/env python3
"""
PracticeRaptor CLI - Practice coding problems with rapid feedback.

Usage:
    python -m clients.cli.main [--task N] [--file solution.py] [--verbose]

Options:
    --task N        Jump to problem #N
    --file FILE     Load solution from file
    --verbose       Verbose output
    --config PATH   Path to config file
    --help          Show this help
"""
import argparse
import sys
from pathlib import Path

from di import load_config, create_container
from .app import CLIApp


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PracticeRaptor CLI - Practice coding problems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m clients.cli.main                    Interactive mode
  python -m clients.cli.main --task 2           Jump to problem #2
  python -m clients.cli.main --task 1 --file solution.py
  python -m clients.cli.main --verbose          Verbose output
        """
    )

    parser.add_argument(
        "--task", "-t",
        type=int,
        help="Problem number"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Solution file path"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=Path("config/config.yaml"),
        help="Config file path"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Load configuration
    config = load_config(args.config)

    # Create DI container
    try:
        container = create_container(config)
    except Exception as e:
        print(f"Error initializing application: {e}", file=sys.stderr)
        return 1

    # Create and run app
    app = CLIApp(container)

    try:
        return app.run(
            task_id=args.task,
            file_path=args.file,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # For multiprocessing on all platforms
    import multiprocessing as mp
    mp.set_start_method("spawn", force=True)

    sys.exit(main())
```

### 8.6. Обновить clients/cli/__init__.py

```python
# clients/cli/__init__.py
"""CLI client for PracticeRaptor."""
from .app import CLIApp
from .main import main

__all__ = [
    "CLIApp",
    "main",
]
```

## Сравнение со старым кодом

| Старый prototype/ | Новый clients/cli/ |
|-------------------|-------------------|
| `main.py` (280 строк) | `main.py` (~60) + `app.py` (~150) |
| `config.py` (Colors + paths) | `colors.py` + `di/config.py` |
| `presenter.py` | `presenter.py` (похоже, но использует core) |
| `input_handler.py` | `input_handler.py` (упрощён) |
| `executor.py` | `adapters/executors/local_executor.py` |
| `solution_validator.py` | `core/services/execution.py` |
| `task_loader.py` | `adapters/storage/json_problem_repository.py` |

## Критерии готовности

- [ ] CLI запускается и работает
- [ ] Весь функционал прототипа сохранён
- [ ] Код использует core services
- [ ] Зависимости из Container
- [ ] Тесты для app.py
- [ ] mypy проходит

## Тесты для Step 8

```python
# tests/unit/clients/cli/test_app.py
import pytest
from unittest.mock import MagicMock, patch

from clients.cli.app import CLIApp
from core.domain.models import Problem, LocalizedText, LanguageSpec
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok


@pytest.fixture
def mock_container():
    container = MagicMock()
    container.default_locale = "en"
    container.problem_repo = MagicMock()
    container.executor = MagicMock()
    return container


@pytest.fixture
def sample_problem():
    return Problem(
        id=1,
        title=LocalizedText({"en": "Two Sum"}),
        description=LocalizedText({"en": "Find two numbers..."}),
        difficulty=Difficulty.EASY,
        tags=("array",),
        examples=(),
        test_cases=(),
        languages=(
            LanguageSpec(
                language=Language.PYTHON,
                function_signature="def two_sum(nums, target):",
                solutions=(),
            ),
        ),
    )


class TestCLIApp:
    def test_run_returns_1_when_no_problems(self, mock_container):
        mock_container.problem_repo.get_all.return_value = ()

        app = CLIApp(mock_container)

        with patch('clients.cli.app.get_all_problems', return_value=()):
            result = app.run()

        assert result == 1

    def test_run_interactive_exits_on_keyboard_interrupt(self, mock_container, sample_problem):
        with patch('clients.cli.app.get_all_problems', return_value=(sample_problem,)):
            with patch('clients.cli.app.display_welcome'):
                with patch.object(CLIApp, '_select_problem', side_effect=KeyboardInterrupt):
                    with patch('clients.cli.app.display_message'):
                        app = CLIApp(mock_container)
                        result = app.run()

        assert result == 0
```

## Миграция данных задач

Текущие JSON-файлы из `prototype/tasks/` нужно скопировать в `data/problems/`:

```bash
mkdir -p data/problems
cp prototype/tasks/*.json data/problems/
```

JSON-формат совместим — `JsonProblemRepository` поддерживает старый формат.

## Следующий шаг

После завершения Step 8 переходите к [Step 9: Testing](./09_testing.md).
