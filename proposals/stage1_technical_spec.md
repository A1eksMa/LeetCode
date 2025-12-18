# Техническое задание: Этап 1 — Прототип

## 1. Общее описание

CLI-приложение для решения алгоритмических задач. Пользователь выбирает задачу из списка, получает условие, пишет решение и отправляет на проверку.

### 1.1. Пользовательский сценарий

```
$ python main.py

╔════════════════════════════════════════╗
║       LeetCode Practice CLI            ║
╚════════════════════════════════════════╝

Доступные задачи:
  [0] Случайная задача
  [1] Two Sum (easy) [array, hash-table]
  [2] Reverse String (easy) [string, two-pointers]
  [3] Valid Palindrome (easy) [string, two-pointers]

Выберите задачу (0-3): 1

────────────────────────────────────────
Задача #1: Two Sum
Сложность: easy
Теги: array, hash-table
────────────────────────────────────────

Дан массив целых чисел nums и целое число target...

Примеры:
  Input: nums = [2, 7, 11, 15], target = 9
  Output: [0, 1]
  Пояснение: nums[0] + nums[1] = 2 + 7 = 9

Сигнатура функции:
  def two_sum(nums: list[int], target: int) -> list[int]:

────────────────────────────────────────

Введите решение (двойной Enter для завершения, !hint для подсказки):
>>> def two_sum(nums, target):
>>>     seen = {}
>>>     for i, num in enumerate(nums):
>>>         if target - num in seen:
>>>             return [seen[target - num], i]
>>>         seen[num] = i
>>>     return []
>>>
>>>

Проверка решения...

✓ Тест 1/7: passed (0.001s)
✓ Тест 2/7: passed (0.001s)
✓ Тест 3/7: passed (0.001s)
✓ Тест 4/7: passed (0.001s)
✓ Тест 5/7: passed (0.001s)
✓ Тест 6/7: passed (0.001s)
✓ Тест 7/7: passed (0.001s)

════════════════════════════════════════
✓ Все тесты пройдены!
  Время выполнения: 0.007s
════════════════════════════════════════

Продолжить? (y/n): y
```

---

## 2. Структура проекта

```
leetcode-prototype/
├── main.py                 # Точка входа, главный цикл приложения
├── task_loader.py          # Загрузка и парсинг JSON-файлов задач
├── task_validator.py       # Валидация JSON-схемы и проверка решений
├── selector.py             # Отображение списка и выбор задачи
├── presenter.py            # Форматирование и вывод задачи пользователю
├── input_handler.py        # Приём многострочного кода от пользователя
├── executor.py             # Выполнение пользовательского кода (multiprocessing)
├── solution_validator.py   # Запуск тестов и сравнение результатов
├── result_reporter.py      # Форматирование и вывод результатов
├── config.py               # Константы и настройки
├── models.py               # Dataclass-модели данных
├── tasks/
│   ├── 1_two_sum.json
│   ├── 2_reverse_string.json
│   └── 3_valid_palindrome.json
└── README.md
```

---

## 3. Модели данных (models.py)

```python
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class Example:
    """Пример из условия задачи."""
    input: dict[str, Any]
    output: Any
    explanation: str | None = None


@dataclass
class TestCase:
    """Тест-кейс для проверки решения."""
    input: dict[str, Any]
    expected: Any
    description: str | None = None  # Описание теста (например, "отрицательные числа")


@dataclass
class Solution:
    """Каноническое решение задачи."""
    name: str
    complexity: str
    code: str


@dataclass
class LanguageSpec:
    """Языково-специфичные данные задачи."""
    function_signature: str
    solutions: list[Solution] = field(default_factory=list)


@dataclass
class Task:
    """Полное представление задачи."""
    id: int
    title: str
    difficulty: Difficulty
    tags: list[str]
    description: str
    examples: list[Example]
    test_cases: list[TestCase]
    languages: dict[str, LanguageSpec] = field(default_factory=dict)

    @property
    def function_name(self) -> str:
        """Извлекает имя функции из сигнатуры."""
        # "def two_sum(..." -> "two_sum"
        sig = self.languages.get("python3", LanguageSpec("")).function_signature
        if sig.startswith("def "):
            return sig[4:].split("(")[0]
        return ""


@dataclass
class TestResult:
    """Результат выполнения одного теста."""
    test_number: int
    status: TestStatus
    execution_time: float
    input_data: dict[str, Any]
    expected: Any
    actual: Any | None = None
    error_message: str | None = None


@dataclass
class ExecutionResult:
    """Полный результат проверки решения."""
    success: bool
    total_tests: int
    passed_tests: int
    total_time: float
    results: list[TestResult]
    error: str | None = None
```

---

## 4. Конфигурация (config.py)

```python
from pathlib import Path

# Пути
BASE_DIR = Path(__file__).parent
TASKS_DIR = BASE_DIR / "tasks"

# Настройки выполнения
EXECUTION_TIMEOUT = 5  # секунд на один тест
TOTAL_TIMEOUT = 30     # секунд на все тесты

# Язык по умолчанию
DEFAULT_LANGUAGE = "python3"

# Форматирование вывода
SEPARATOR = "─" * 40
DOUBLE_SEPARATOR = "═" * 40

# Цвета (ANSI escape codes)
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
```

---

## 5. Спецификация модулей

### 5.1. task_loader.py — Загрузка задач

**Назначение:** Чтение JSON-файлов из директории tasks/, парсинг и преобразование в dataclass-модели.

```python
"""
Модуль загрузки задач из JSON-файлов.

Функции:
- load_task(filepath) -> Task
- load_all_tasks(directory) -> list[Task]
- get_task_files(directory) -> list[Path]
"""

from pathlib import Path
from models import Task, Example, TestCase, Solution, LanguageSpec, Difficulty


def get_task_files(directory: Path) -> list[Path]:
    """
    Получает список JSON-файлов задач из директории.

    Args:
        directory: Путь к директории с задачами.

    Returns:
        Список путей к JSON-файлам, отсортированный по имени.

    Example:
        >>> get_task_files(Path("tasks"))
        [Path("tasks/1_two_sum.json"), Path("tasks/2_reverse_string.json")]
    """
    ...


def parse_example(data: dict) -> Example:
    """
    Парсит один пример из JSON.

    Args:
        data: Словарь с ключами input, output, explanation (опционально).

    Returns:
        Объект Example.
    """
    ...


def parse_test_case(data: dict) -> TestCase:
    """
    Парсит один тест-кейс из JSON.

    Args:
        data: Словарь с ключами input, expected.

    Returns:
        Объект TestCase.
    """
    ...


def parse_solution(data: dict) -> Solution:
    """
    Парсит одно решение из JSON.

    Args:
        data: Словарь с ключами name, complexity, code.

    Returns:
        Объект Solution.
    """
    ...


def parse_language_spec(data: dict) -> LanguageSpec:
    """
    Парсит языково-специфичные данные.

    Args:
        data: Словарь с ключами function_signature, solutions.

    Returns:
        Объект LanguageSpec.
    """
    ...


def load_task(filepath: Path) -> Task:
    """
    Загружает одну задачу из JSON-файла.

    Args:
        filepath: Путь к JSON-файлу.

    Returns:
        Объект Task с полными данными задачи.

    Raises:
        FileNotFoundError: Файл не найден.
        json.JSONDecodeError: Невалидный JSON.
        KeyError: Отсутствует обязательное поле.

    Example:
        >>> task = load_task(Path("tasks/1_two_sum.json"))
        >>> task.title
        "Two Sum"
    """
    ...


def load_all_tasks(directory: Path) -> list[Task]:
    """
    Загружает все задачи из директории.

    Args:
        directory: Путь к директории с JSON-файлами.

    Returns:
        Список объектов Task, отсортированный по id.

    Raises:
        FileNotFoundError: Директория не найдена.

    Example:
        >>> tasks = load_all_tasks(Path("tasks"))
        >>> len(tasks)
        3
    """
    ...
```

---

### 5.2. selector.py — Выбор задачи

**Назначение:** Отображение списка задач и получение выбора пользователя.

```python
"""
Модуль выбора задачи из списка.

Функции:
- display_task_list(tasks) -> None
- get_user_choice(max_value) -> int
- select_task(tasks) -> Task
- select_random_task(tasks) -> Task
"""

import random
from models import Task


def format_task_item(task: Task, index: int) -> str:
    """
    Форматирует одну строку списка задач.

    Args:
        task: Объект задачи.
        index: Номер в списке (для отображения).

    Returns:
        Отформатированная строка.

    Example:
        >>> format_task_item(task, 1)
        "  [1] Two Sum (easy) [array, hash-table]"
    """
    ...


def display_task_list(tasks: list[Task]) -> None:
    """
    Выводит список доступных задач.

    Формат вывода:
        Доступные задачи:
          [0] Случайная задача
          [1] Two Sum (easy) [array, hash-table]
          [2] Reverse String (easy) [string]
          ...

    Args:
        tasks: Список задач для отображения.
    """
    ...


def get_user_choice(min_value: int, max_value: int, prompt: str = "Выберите задачу") -> int:
    """
    Запрашивает у пользователя выбор числа из диапазона.

    Args:
        min_value: Минимальное допустимое значение.
        max_value: Максимальное допустимое значение.
        prompt: Текст приглашения к вводу.

    Returns:
        Выбранное число.

    Note:
        Повторяет запрос при невалидном вводе.
    """
    ...


def select_random_task(tasks: list[Task]) -> Task:
    """
    Выбирает случайную задачу из списка.

    Args:
        tasks: Список задач.

    Returns:
        Случайно выбранная задача.
    """
    ...


def select_task(tasks: list[Task]) -> Task:
    """
    Полный flow выбора задачи: показывает список, получает выбор.

    Args:
        tasks: Список доступных задач.

    Returns:
        Выбранная задача (или случайная, если выбран 0).

    Example:
        >>> task = select_task(tasks)
        # Пользователь видит список, вводит номер
        >>> task.title
        "Two Sum"
    """
    ...
```

---

### 5.3. presenter.py — Отображение задачи

**Назначение:** Форматирование и вывод условия задачи пользователю.

```python
"""
Модуль отображения задачи.

Функции:
- present_task(task, language) -> None
- format_header(task) -> str
- format_description(task) -> str
- format_examples(task) -> str
- format_signature(task, language) -> str
"""

from models import Task, Example


def format_header(task: Task) -> str:
    """
    Форматирует заголовок задачи.

    Args:
        task: Объект задачи.

    Returns:
        Строка вида:
        ────────────────────────────────────────
        Задача #1: Two Sum
        Сложность: easy
        Теги: array, hash-table
        ────────────────────────────────────────
    """
    ...


def format_description(description: str) -> str:
    """
    Форматирует описание задачи.

    Args:
        description: Текст описания.

    Returns:
        Отформатированный текст с переносами строк.
    """
    ...


def format_example(example: Example, index: int) -> str:
    """
    Форматирует один пример.

    Args:
        example: Объект примера.
        index: Номер примера.

    Returns:
        Строка вида:
        Пример 1:
          Input: nums = [2, 7, 11, 15], target = 9
          Output: [0, 1]
          Пояснение: nums[0] + nums[1] = 2 + 7 = 9
    """
    ...


def format_examples(examples: list[Example]) -> str:
    """
    Форматирует все примеры задачи.

    Args:
        examples: Список примеров.

    Returns:
        Отформатированная строка со всеми примерами.
    """
    ...


def format_signature(task: Task, language: str = "python3") -> str:
    """
    Форматирует сигнатуру функции.

    Args:
        task: Объект задачи.
        language: Язык программирования.

    Returns:
        Строка вида:
        Сигнатура функции:
          def two_sum(nums: list[int], target: int) -> list[int]:
    """
    ...


def present_task(task: Task, language: str = "python3") -> None:
    """
    Выводит полное условие задачи в консоль.

    Args:
        task: Объект задачи.
        language: Язык программирования для сигнатуры.

    Note:
        Выводит: заголовок, описание, примеры, сигнатуру.
    """
    ...
```

---

### 5.4. input_handler.py — Ввод кода пользователя

**Назначение:** Приём многострочного кода от пользователя через stdin с поддержкой специальных команд.

```python
"""
Модуль обработки пользовательского ввода.

Функции:
- read_user_code(task, previous_code) -> InputResult
- read_code_from_file(filepath) -> str
- validate_code_syntax(code) -> tuple[bool, str | None]
- parse_signature_args(signature) -> list[str]

Специальные команды во время ввода:
- !hint    — показать подсказку (каноническое решение)
- !reset   — очистить введённый код и начать заново
- !cancel  — отменить ввод и вернуться к выбору задачи
"""

from pathlib import Path
from dataclasses import dataclass
from models import Task


@dataclass
class InputResult:
    """Результат ввода кода пользователем."""
    code: str | None
    cancelled: bool = False
    hint_requested: bool = False


def read_user_code(
    task: Task,
    previous_code: str | None = None,
    language: str = "python3"
) -> InputResult:
    """
    Читает многострочный код от пользователя.

    Ввод завершается двумя пустыми строками подряд (двойной Enter).
    Поддерживает специальные команды: !hint, !reset, !cancel.

    Args:
        task: Текущая задача (для показа подсказок).
        previous_code: Предыдущий код (для редактирования после ошибки).
        language: Язык программирования.

    Returns:
        InputResult с кодом или флагами состояния.

    Example:
        >>> result = read_user_code(task, previous_code="def foo(): pass")
        Введите решение (двойной Enter для завершения, !hint для подсказки):

        Предыдущий код (редактируйте или введите новый):
        ┌──────────────────────────────────────
        │ def foo(): pass
        └──────────────────────────────────────

        >>> def two_sum(nums, target):
        >>>     seen = {}
        >>>     for i, num in enumerate(nums):
        >>>         if target - num in seen:
        >>>             return [seen[target - num], i]
        >>>         seen[num] = i
        >>>     return []
        >>>
        >>>
        >>> result.code
        "def two_sum(nums, target):\n    ..."

    Note:
        - Одна пустая строка допустима внутри кода
        - Две пустые строки подряд завершают ввод
        - !hint показывает следующую подсказку из solutions
    """
    ...


def read_code_from_file(filepath: Path) -> str:
    """
    Читает код из файла.

    Args:
        filepath: Путь к файлу с кодом.

    Returns:
        Содержимое файла.

    Raises:
        FileNotFoundError: Файл не найден.

    Note:
        Для будущего расширения (ввод через файл).
    """
    ...


def validate_code_syntax(code: str) -> tuple[bool, str | None]:
    """
    Проверяет синтаксическую корректность кода.

    Args:
        code: Python-код для проверки.

    Returns:
        Кортеж (is_valid, error_message).
        Если код валиден: (True, None)
        Если невалиден: (False, "SyntaxError: ...")

    Example:
        >>> validate_code_syntax("def foo(: pass")
        (False, "SyntaxError: invalid syntax (line 1)")
    """
    ...


def extract_function_name(code: str) -> str | None:
    """
    Извлекает имя определённой функции из кода.

    Args:
        code: Python-код.

    Returns:
        Имя первой определённой функции или None.

    Example:
        >>> extract_function_name("def my_func(x): return x")
        "my_func"
    """
    ...


def parse_signature_args(signature: str) -> list[str]:
    """
    Извлекает имена аргументов из сигнатуры функции.

    Args:
        signature: Сигнатура функции Python.

    Returns:
        Список имён аргументов в порядке их определения.

    Example:
        >>> parse_signature_args("def two_sum(nums: list[int], target: int) -> list[int]:")
        ["nums", "target"]

        >>> parse_signature_args("def solve(matrix, k, threshold=0.5):")
        ["matrix", "k", "threshold"]

    Note:
        Используется для правильного порядка передачи аргументов
        из test_case.input в вызов функции.
    """
    ...


def show_hint(task: Task, hint_index: int, language: str = "python3") -> int:
    """
    Показывает подсказку (каноническое решение) пользователю.

    Args:
        task: Текущая задача.
        hint_index: Индекс текущей подсказки (0, 1, 2...).
        language: Язык программирования.

    Returns:
        Новый hint_index (для следующей подсказки).

    Note:
        Показывает решения по порядку: сначала простое (Brute Force),
        потом оптимальное. Предупреждает перед показом.
    """
    ...
```

---

### 5.5. executor.py — Выполнение кода

**Назначение:** Безопасное выполнение пользовательского кода с ограничениями через multiprocessing.

```python
"""
Модуль выполнения пользовательского кода.

Использует multiprocessing для надёжного таймаута и изоляции.
Работает на всех платформах (Unix, Windows, macOS).

Функции:
- execute_code(code, function_name, args, arg_order, timeout) -> ExecutionOutput
- create_sandbox_globals() -> dict
- run_in_process(code, function_name, args, arg_order, result_queue) -> None
"""

import multiprocessing as mp
from dataclasses import dataclass
from typing import Any
from queue import Empty


@dataclass
class ExecutionOutput:
    """Результат выполнения кода."""
    success: bool
    result: Any | None = None
    error_type: str | None = None
    error_message: str | None = None
    execution_time: float = 0.0


def create_sandbox_globals() -> dict:
    """
    Создаёт ограниченное глобальное окружение для exec().

    Returns:
        Словарь с безопасным набором built-in функций.

    Note:
        Исключает: open, exec, eval, __import__, compile и др.
        Включает: len, range, enumerate, zip, map, filter, sorted,
                  min, max, sum, abs, all, any, reversed, etc.
    """
    ...


def run_in_process(
    code: str,
    function_name: str,
    args: dict[str, Any],
    arg_order: list[str],
    result_queue: mp.Queue
) -> None:
    """
    Выполняет код в отдельном процессе (worker function).

    Args:
        code: Пользовательский Python-код.
        function_name: Имя функции для вызова.
        args: Аргументы функции (словарь).
        arg_order: Порядок аргументов (из сигнатуры).
        result_queue: Очередь для возврата результата.

    Note:
        Эта функция запускается в дочернем процессе.
        Результат или ошибка передаётся через Queue.
    """
    ...


def execute_code(
    code: str,
    function_name: str,
    args: dict[str, Any],
    arg_order: list[str],
    timeout: float = 5.0
) -> ExecutionOutput:
    """
    Выполняет пользовательский код и вызывает функцию.

    Создаёт отдельный процесс, выполняет код, ждёт результат.
    При превышении таймаута — убивает процесс через terminate().

    Args:
        code: Пользовательский Python-код.
        function_name: Имя функции для вызова.
        args: Аргументы функции (словарь).
        arg_order: Порядок аргументов (из parse_signature_args).
        timeout: Лимит времени на выполнение.

    Returns:
        ExecutionOutput с результатом или ошибкой.

    Example:
        >>> result = execute_code(
        ...     code="def add(a, b): return a + b",
        ...     function_name="add",
        ...     args={"a": 2, "b": 3},
        ...     arg_order=["a", "b"]
        ... )
        >>> result.success
        True
        >>> result.result
        5

    Note:
        - Использует multiprocessing.Process для изоляции
        - Process.terminate() надёжно убивает зависший код
        - Работает на всех платформах
    """
    ...


def prepare_arguments(test_input: dict[str, Any]) -> dict[str, Any]:
    """
    Подготавливает аргументы для вызова функции.

    Args:
        test_input: Входные данные теста.

    Returns:
        Словарь аргументов (глубокая копия для изоляции).

    Note:
        Создаёт копии мутабельных объектов (списки, словари),
        чтобы пользовательский код не мог повлиять на оригинал.
    """
    ...
```

---

### 5.6. solution_validator.py — Валидация решений

**Назначение:** Запуск тестов и сравнение результатов с ожидаемыми.

```python
"""
Модуль валидации пользовательских решений.

Функции:
- validate_solution(code, task) -> ExecutionResult
- run_single_test(code, function_name, test_case, test_number, arg_order) -> TestResult
- compare_results(actual, expected) -> bool
"""

from models import Task, TestCase, TestResult, ExecutionResult, TestStatus
from input_handler import parse_signature_args


def compare_results(actual: Any, expected: Any) -> bool:
    """
    Сравнивает фактический результат с ожидаемым.

    Args:
        actual: Результат выполнения пользовательского кода.
        expected: Ожидаемый результат из теста.

    Returns:
        True если результаты эквивалентны.

    Note:
        Обрабатывает особые случаи:
        - Списки: сравнение как множества (если порядок не важен)
        - Float: сравнение с погрешностью
        - None: строгое сравнение
    """
    ...


def run_single_test(
    code: str,
    function_name: str,
    test_case: TestCase,
    test_number: int
) -> TestResult:
    """
    Выполняет один тест.

    Args:
        code: Пользовательский код.
        function_name: Имя функции.
        test_case: Тест-кейс с input и expected.
        test_number: Номер теста (для отчёта).

    Returns:
        TestResult с результатом выполнения.
    """
    ...


def validate_solution(
    code: str,
    task: Task,
    language: str = "python3",
    stop_on_first_failure: bool = True
) -> ExecutionResult:
    """
    Проверяет решение на всех тест-кейсах.

    Args:
        code: Пользовательский код.
        task: Объект задачи с тестами.
        language: Язык программирования.
        stop_on_first_failure: Остановиться при первой ошибке.

    Returns:
        ExecutionResult с полными результатами проверки.

    Example:
        >>> result = validate_solution(user_code, task)
        >>> result.success
        True
        >>> result.passed_tests
        7
    """
    ...
```

---

### 5.7. task_validator.py — Валидация задач

**Назначение:** Валидация JSON-схемы файлов задач и проверка канонических решений на тестах. Используется при добавлении новых задач в систему.

```python
"""
Модуль валидации файлов задач.

Два режима работы:
1. Валидация схемы JSON — проверка структуры и обязательных полей
2. Валидация решений — проверка канонических решений на тестах

Функции:
- validate_task_file(filepath) -> ValidationResult
- validate_task_schema(data) -> list[str]
- validate_solutions(task) -> list[SolutionValidationResult]
- validate_all_tasks(directory) -> list[ValidationResult]

CLI:
    python task_validator.py tasks/1_two_sum.json     # одна задача
    python task_validator.py tasks/                    # все задачи
    python task_validator.py --schema-only tasks/     # только схема
"""

from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SolutionValidationResult:
    """Результат валидации одного решения."""
    solution_name: str
    passed: bool
    passed_tests: int
    total_tests: int
    error: str | None = None


@dataclass
class ValidationResult:
    """Результат валидации файла задачи."""
    filepath: Path
    valid: bool
    schema_errors: list[str] = field(default_factory=list)
    solution_results: list[SolutionValidationResult] = field(default_factory=list)


# Схема обязательных полей JSON
REQUIRED_FIELDS = {
    "root": ["id", "title", "difficulty", "tags", "description", "examples", "test_cases"],
    "example": ["input", "output"],
    "test_case": ["input", "expected"],
    "language_spec": ["function_signature", "solutions"],
    "solution": ["name", "complexity", "code"]
}

VALID_DIFFICULTIES = ["easy", "medium", "hard"]


def validate_task_schema(data: dict) -> list[str]:
    """
    Проверяет структуру JSON на соответствие схеме.

    Args:
        data: Загруженные данные задачи.

    Returns:
        Список ошибок (пустой если всё ок).

    Example:
        >>> errors = validate_task_schema({"id": 1, "title": "Test"})
        >>> errors
        ["Отсутствует обязательное поле: difficulty",
         "Отсутствует обязательное поле: tags", ...]
    """
    ...


def validate_solution_code(task: "Task", solution: "Solution") -> SolutionValidationResult:
    """
    Проверяет одно каноническое решение на всех тестах.

    Args:
        task: Объект задачи.
        solution: Каноническое решение для проверки.

    Returns:
        SolutionValidationResult с результатами.

    Note:
        Использует solution_validator.validate_solution внутри.
    """
    ...


def validate_solutions(task: "Task", language: str = "python3") -> list[SolutionValidationResult]:
    """
    Проверяет все канонические решения задачи.

    Args:
        task: Объект задачи.
        language: Язык программирования.

    Returns:
        Список результатов для каждого решения.
    """
    ...


def validate_task_file(
    filepath: Path,
    check_solutions: bool = True
) -> ValidationResult:
    """
    Полная валидация файла задачи.

    Args:
        filepath: Путь к JSON-файлу.
        check_solutions: Проверять ли решения на тестах.

    Returns:
        ValidationResult с полной информацией.

    Example:
        >>> result = validate_task_file(Path("tasks/1_two_sum.json"))
        >>> result.valid
        True
        >>> result.solution_results[0].passed
        True
    """
    ...


def validate_all_tasks(
    directory: Path,
    check_solutions: bool = True
) -> list[ValidationResult]:
    """
    Валидирует все задачи в директории.

    Args:
        directory: Путь к директории с задачами.
        check_solutions: Проверять ли решения.

    Returns:
        Список ValidationResult для каждого файла.
    """
    ...


def print_validation_report(results: list[ValidationResult]) -> None:
    """
    Выводит отчёт о валидации в консоль.

    Формат вывода:
        Валидация задач
        ════════════════════════════════════════

        ✓ tasks/1_two_sum.json
          Схема: OK
          Решения:
            ✓ Brute Force: 7/7 тестов
            ✓ Hash Map (один проход): 7/7 тестов
            ✓ Hash Map (два прохода): 7/7 тестов

        ✗ tasks/2_broken.json
          Схема: 2 ошибки
            - Отсутствует поле: python3.function_signature
            - Неверное значение difficulty: "super-hard"

        ════════════════════════════════════════
        Итого: 2/3 задач валидны
    """
    ...


if __name__ == "__main__":
    # CLI интерфейс для валидации
    import argparse
    ...
```

---

### 5.8. result_reporter.py — Отображение результатов

**Назначение:** Форматирование и вывод результатов проверки.

```python
"""
Модуль отображения результатов.

Функции:
- report_results(execution_result) -> None
- format_test_result(test_result) -> str
- format_summary(execution_result) -> str
- format_error(test_result) -> str
"""

from models import ExecutionResult, TestResult, TestStatus


def format_test_result(result: TestResult, verbose: bool = False) -> str:
    """
    Форматирует результат одного теста.

    Args:
        result: Результат теста.
        verbose: Показывать детали (input/output).

    Returns:
        Строка вида:
        - Успех: "✓ Тест 1/7: passed (0.001s)"
        - Провал: "✗ Тест 3/7: failed (0.002s)"
        - Ошибка: "✗ Тест 5/7: error - NameError: name 'x' is not defined"
    """
    ...


def format_error_details(result: TestResult) -> str:
    """
    Форматирует детали ошибки.

    Args:
        result: Результат теста с ошибкой.

    Returns:
        Строка вида:
          Input: {"nums": [1, 2, 3], "target": 5}
          Expected: [0, 2]
          Actual: [1, 2]

        Или для runtime error:
          Error: NameError: name 'x' is not defined
    """
    ...


def format_summary(result: ExecutionResult) -> str:
    """
    Форматирует итоговую сводку.

    Args:
        result: Полный результат выполнения.

    Returns:
        Строка вида (успех):
        ════════════════════════════════════════
        ✓ Все тесты пройдены!
          Время выполнения: 0.007s
        ════════════════════════════════════════

        Или (провал):
        ════════════════════════════════════════
        ✗ Тесты не пройдены: 5/7
          Время выполнения: 0.003s
        ════════════════════════════════════════
    """
    ...


def report_results(result: ExecutionResult, verbose: bool = False) -> None:
    """
    Выводит полный отчёт о результатах.

    Args:
        result: Результат выполнения всех тестов.
        verbose: Показывать детали каждого теста.

    Note:
        При провале теста автоматически показывает детали ошибки.
    """
    ...
```

---

### 5.9. main.py — Главный модуль

**Назначение:** Точка входа, главный цикл приложения.

```python
"""
Главный модуль приложения LeetCode Practice CLI.

Запуск: python main.py [--task N] [--file solution.py]

Опции:
    --task N     Выбрать задачу по номеру (пропустить меню)
    --file FILE  Загрузить решение из файла
    --verbose    Подробный вывод результатов
    --help       Показать справку
"""

import argparse
import sys
from pathlib import Path

from config import TASKS_DIR, DEFAULT_LANGUAGE
from task_loader import load_all_tasks
from selector import select_task
from presenter import present_task
from input_handler import read_user_code, read_code_from_file, validate_code_syntax
from solution_validator import validate_solution
from result_reporter import report_results


def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки.

    Returns:
        Объект с аргументами: task, file, verbose.
    """
    ...


def display_welcome() -> None:
    """
    Выводит приветственный баннер.
    """
    ...


def ask_continue() -> bool:
    """
    Спрашивает пользователя о продолжении.

    Returns:
        True если пользователь хочет продолжить.
    """
    ...


def run_solve_flow(task: Task, code: str | None = None, verbose: bool = False) -> bool:
    """
    Выполняет полный flow решения одной задачи.

    Args:
        task: Задача для решения.
        code: Код решения (если None, запрашивается у пользователя).
        verbose: Подробный вывод.

    Returns:
        True если все тесты пройдены.
    """
    ...


def main_loop(tasks: list[Task], verbose: bool = False) -> None:
    """
    Главный цикл приложения.

    Args:
        tasks: Список доступных задач.
        verbose: Подробный вывод.

    Note:
        Цикл: выбор задачи -> решение -> результаты -> продолжить?
    """
    ...


def main() -> int:
    """
    Точка входа приложения.

    Returns:
        Exit code: 0 при успехе, 1 при ошибке.
    """
    args = parse_args()

    # Загрузка задач
    try:
        tasks = load_all_tasks(TASKS_DIR)
    except FileNotFoundError:
        print(f"Ошибка: директория {TASKS_DIR} не найдена")
        return 1

    if not tasks:
        print("Ошибка: задачи не найдены")
        return 1

    display_welcome()

    # Режим с указанным файлом решения
    if args.file:
        code = read_code_from_file(Path(args.file))
        task = tasks[args.task - 1] if args.task else select_task(tasks)
        success = run_solve_flow(task, code, args.verbose)
        return 0 if success else 1

    # Интерактивный режим
    main_loop(tasks, args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 6. Диаграмма взаимодействия модулей

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                  main.py                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                       │
│  │ parse_args  │───►│main_loop    │───►│run_solve_   │                       │
│  └─────────────┘    └─────────────┘    │   flow      │                       │
│                                         └──────┬──────┘                       │
└────────────────────────────────────────────────┼──────────────────────────────┘
                                                 │
         ┌───────────────┬───────────────────────┼───────────────────────┐
         │               │                       │                       │
         ▼               ▼                       ▼                       ▼
┌─────────────┐  ┌─────────────┐        ┌─────────────┐         ┌─────────────┐
│task_loader  │  │  selector   │        │  presenter  │         │input_handler│
│             │  │             │        │             │         │             │
│load_all_    │  │select_task  │        │present_task │         │read_user_   │
│  tasks()    │  │display_list │        │format_*     │         │  code()     │
└──────┬──────┘  └─────────────┘        └─────────────┘         │parse_sig_   │
       │                                                         │  args()     │
       │                                                         │show_hint()  │
       │         ┌──────────────────────────────────────────────┴─────────────┘
       │         │
       ▼         ▼
┌─────────────────────┐         ┌─────────────────────┐
│ solution_validator  │────────►│     executor        │
│                     │         │                     │
│ validate_solution() │         │ execute_code()      │
│ run_single_test()   │         │ run_in_process()    │
│ compare_results()   │         │ (multiprocessing)   │
└──────────┬──────────┘         └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  result_reporter    │
│                     │
│ report_results()    │
│ format_summary()    │
└─────────────────────┘


┌─────────────────────┐         ┌─────────────────────┐
│  task_validator     │         │     config.py       │
│  (standalone CLI)   │         │                     │
│                     │         │ TASKS_DIR,          │
│ validate_task_file()│         │ EXECUTION_TIMEOUT,  │
│ validate_schema()   │         │ Colors              │
│ validate_solutions()│         │                     │
└─────────────────────┘         └─────────────────────┘

┌─────────────────────┐
│     models.py       │
│                     │
│ Task, TestCase,     │
│ TestResult,         │
│ ExecutionResult,    │
│ InputResult         │
└─────────────────────┘
```

---

## 7. Порядок запуска и CLI интерфейс

### 7.1. Базовый запуск
```bash
python main.py
```
Интерактивный режим: выбор задачи из меню, ввод решения с клавиатуры.

### 7.2. Запуск с параметрами
```bash
# Сразу перейти к задаче #2
python main.py --task 2

# Загрузить решение из файла
python main.py --task 1 --file solution.py

# Подробный вывод результатов
python main.py --verbose

# Справка
python main.py --help
```

### 7.3. Примеры использования

**Пример 1: Интерактивный режим**
```
$ python main.py

╔════════════════════════════════════════╗
║       LeetCode Practice CLI            ║
╚════════════════════════════════════════╝

Доступные задачи:
  [0] Случайная задача
  [1] Two Sum (easy) [array, hash-table]
  [2] Reverse String (easy) [string, two-pointers]
  [3] Valid Palindrome (easy) [string, two-pointers]

Выберите задачу (0-3): 1
```

**Пример 2: Ошибка синтаксиса**
```
Введите ваше решение (пустая строка + Enter для завершения):
>>> def two_sum(nums, target)
>>>     return [0, 1]
>>>

✗ Синтаксическая ошибка:
  SyntaxError: expected ':' (line 1)

Попробуйте ещё раз.
```

**Пример 3: Провал теста**
```
Проверка решения...

✓ Тест 1/7: passed (0.001s)
✓ Тест 2/7: passed (0.001s)
✗ Тест 3/7: failed (0.001s)

  Input: {"nums": [3, 3], "target": 6}
  Expected: [0, 1]
  Actual: [0, 0]

════════════════════════════════════════
✗ Тесты не пройдены: 2/7
  Время выполнения: 0.003s
════════════════════════════════════════
```

**Пример 4: Timeout**
```
Проверка решения...

✓ Тест 1/7: passed (0.001s)
✗ Тест 2/7: timeout (5.000s)

  Error: превышен лимит времени (5 сек)

════════════════════════════════════════
✗ Тесты не пройдены: 1/7
  Время выполнения: 5.001s
════════════════════════════════════════
```

---

## 8. Обработка ошибок

### 8.1. Классификация ошибок

| Тип ошибки | Источник | Обработка |
|------------|----------|-----------|
| SyntaxError | Пользовательский код | Показать строку и позицию ошибки, предложить повторить ввод |
| NameError | Пользовательский код | Показать сообщение, предложить повторить |
| TypeError | Пользовательский код | Показать сообщение, предложить повторить |
| TimeoutError | executor.py | Прервать тест, показать лимит времени |
| FileNotFoundError | task_loader.py | Сообщить об отсутствии файла/директории |
| JSONDecodeError | task_loader.py | Сообщить о невалидном JSON |
| KeyboardInterrupt | Пользователь | Корректно завершить программу |

### 8.2. Стратегия обработки

```python
# В main.py
try:
    main_loop(tasks)
except KeyboardInterrupt:
    print("\n\nДо свидания!")
    sys.exit(0)
except Exception as e:
    print(f"\nНепредвиденная ошибка: {e}")
    sys.exit(1)
```

---

## 9. Расширяемость

### 9.1. Добавление нового языка
```python
# В models.py - уже поддерживается через languages dict
task.languages["go"] = LanguageSpec(
    function_signature="func twoSum(nums []int, target int) []int",
    solutions=[...]
)

# В executor.py - добавить executor для Go
# В config.py - добавить настройки для Go
```

### 9.2. Добавление фильтров
```python
# В selector.py
def filter_tasks(
    tasks: list[Task],
    difficulty: Difficulty | None = None,
    tags: list[str] | None = None
) -> list[Task]:
    """Фильтрует задачи по критериям."""
    ...
```

### 9.3. Добавление статистики (для этапа 2)
```python
# Новый модуль stats.py
def save_submission(user_id: str, task_id: int, result: ExecutionResult) -> None:
    ...

def get_user_stats(user_id: str) -> dict:
    ...
```

---

## 10. Критерии приёмки

### Основной функционал
- [ ] CLI запускается и показывает список задач
- [ ] Выбор задачи работает (включая случайную)
- [ ] Условие задачи отображается корректно
- [ ] Многострочный ввод кода работает (двойной Enter для завершения)
- [ ] Синтаксические ошибки перехватываются до выполнения
- [ ] Тесты выполняются последовательно
- [ ] Таймаут срабатывает корректно (multiprocessing)
- [ ] Результаты отображаются понятно
- [ ] Программа корректно завершается по Ctrl+C

### Новые функции
- [ ] Команда `!hint` показывает канонические решения
- [ ] После ошибки показывается предыдущий код для редактирования
- [ ] Парсинг сигнатуры корректно определяет порядок аргументов
- [ ] Команды `!reset` и `!cancel` работают

### Валидатор задач
- [ ] `python task_validator.py tasks/` валидирует все задачи
- [ ] Валидация схемы JSON выявляет отсутствующие поля
- [ ] Валидация решений проверяет канонические решения на тестах
- [ ] Отчёт о валидации выводится в понятном формате

### Качество кода
- [ ] Все модули реализованы согласно спецификации
- [ ] Код соответствует PEP 8
- [ ] Все функции имеют docstrings
- [ ] Type hints используются везде
