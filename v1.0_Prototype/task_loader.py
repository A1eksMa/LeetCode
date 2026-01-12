"""
Модуль загрузки задач из JSON-файлов.

Функции:
- load_task(filepath) -> Task
- load_all_tasks(directory) -> list[Task]
- get_task_files(directory) -> list[Path]
"""

import json
from pathlib import Path

from models import (
    Task, Example, TestCase, Solution,
    LanguageSpec, Difficulty
)


def get_task_files(directory: Path) -> list[Path]:
    """
    Получает список JSON-файлов задач из директории.

    Args:
        directory: Путь к директории с задачами.

    Returns:
        Список путей к JSON-файлам, отсортированный по имени.

    Raises:
        FileNotFoundError: Директория не найдена.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Директория не найдена: {directory}")

    files = sorted(directory.glob("*.json"))
    return files


def parse_example(data: dict) -> Example:
    """
    Парсит один пример из JSON.

    Args:
        data: Словарь с ключами input, output, explanation (опционально).

    Returns:
        Объект Example.
    """
    return Example(
        input=data["input"],
        output=data["output"],
        explanation=data.get("explanation")
    )


def parse_test_case(data: dict) -> TestCase:
    """
    Парсит один тест-кейс из JSON.

    Args:
        data: Словарь с ключами input, expected, description (опционально).

    Returns:
        Объект TestCase.
    """
    return TestCase(
        input=data["input"],
        expected=data["expected"],
        description=data.get("description")
    )


def parse_solution(data: dict) -> Solution:
    """
    Парсит одно решение из JSON.

    Args:
        data: Словарь с ключами name, complexity, code.

    Returns:
        Объект Solution.
    """
    return Solution(
        name=data["name"],
        complexity=data["complexity"],
        code=data["code"]
    )


def parse_language_spec(data: dict) -> LanguageSpec:
    """
    Парсит языково-специфичные данные.

    Args:
        data: Словарь с ключами function_signature, solutions.

    Returns:
        Объект LanguageSpec.
    """
    solutions = [parse_solution(s) for s in data.get("solutions", [])]
    return LanguageSpec(
        function_signature=data["function_signature"],
        solutions=solutions
    )


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
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Парсинг базовых полей
    difficulty = Difficulty(data["difficulty"])
    examples = [parse_example(e) for e in data["examples"]]
    test_cases = [parse_test_case(t) for t in data["test_cases"]]

    # Парсинг языковых спецификаций
    languages = {}
    for lang in ["python3", "go", "java", "javascript"]:
        if lang in data:
            languages[lang] = parse_language_spec(data[lang])

    return Task(
        id=data["id"],
        title=data["title"],
        difficulty=difficulty,
        tags=data["tags"],
        description=data["description"],
        examples=examples,
        test_cases=test_cases,
        languages=languages
    )


def load_all_tasks(directory: Path) -> list[Task]:
    """
    Загружает все задачи из директории.

    Args:
        directory: Путь к директории с JSON-файлами.

    Returns:
        Список объектов Task, отсортированный по id.

    Raises:
        FileNotFoundError: Директория не найдена.
    """
    files = get_task_files(directory)
    tasks = []

    for filepath in files:
        try:
            task = load_task(filepath)
            tasks.append(task)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка загрузки {filepath}: {e}")
            continue

    # Сортировка по id
    tasks.sort(key=lambda t: t.id)
    return tasks
