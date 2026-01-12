"""
Модели данных для LeetCode Practice CLI.

Содержит dataclass-определения для задач, тестов и результатов.
"""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class Difficulty(Enum):
    """Уровень сложности задачи."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TestStatus(Enum):
    """Статус выполнения теста."""
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
    description: str | None = None


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
        """Извлекает имя функции из сигнатуры Python."""
        lang_spec = self.languages.get("python3")
        if not lang_spec:
            return ""
        sig = lang_spec.function_signature
        if sig.startswith("def "):
            return sig[4:].split("(")[0]
        return ""

    def get_signature(self, language: str = "python3") -> str:
        """Возвращает сигнатуру функции для указанного языка."""
        lang_spec = self.languages.get(language)
        if lang_spec:
            return lang_spec.function_signature
        return ""

    def get_solutions(self, language: str = "python3") -> list[Solution]:
        """Возвращает список канонических решений для указанного языка."""
        lang_spec = self.languages.get(language)
        if lang_spec:
            return lang_spec.solutions
        return []


@dataclass
class TestResult:
    """Результат выполнения одного теста."""
    test_number: int
    total_tests: int
    status: TestStatus
    execution_time: float
    input_data: dict[str, Any]
    expected: Any
    actual: Any | None = None
    error_message: str | None = None
    description: str | None = None


@dataclass
class ExecutionResult:
    """Полный результат проверки решения."""
    success: bool
    total_tests: int
    passed_tests: int
    total_time: float
    results: list[TestResult]
    error: str | None = None


@dataclass
class InputResult:
    """Результат ввода кода пользователем."""
    code: str | None
    cancelled: bool = False
    show_hint: bool = False
