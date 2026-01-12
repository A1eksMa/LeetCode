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

import json
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, field

from models import Task, Solution
from task_loader import load_task
from solution_validator import validate_solution
from config import Colors, DOUBLE_SEPARATOR


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
    """
    errors = []

    # Проверка корневых полей
    for field in REQUIRED_FIELDS["root"]:
        if field not in data:
            errors.append(f"Отсутствует обязательное поле: {field}")

    # Проверка difficulty
    if "difficulty" in data:
        if data["difficulty"] not in VALID_DIFFICULTIES:
            errors.append(f"Неверное значение difficulty: '{data['difficulty']}'. "
                         f"Допустимые: {VALID_DIFFICULTIES}")

    # Проверка tags
    if "tags" in data:
        if not isinstance(data["tags"], list):
            errors.append("Поле 'tags' должно быть списком")
        elif not data["tags"]:
            errors.append("Поле 'tags' не должно быть пустым")

    # Проверка examples
    if "examples" in data:
        if not isinstance(data["examples"], list):
            errors.append("Поле 'examples' должно быть списком")
        else:
            for i, example in enumerate(data["examples"]):
                for field in REQUIRED_FIELDS["example"]:
                    if field not in example:
                        errors.append(f"examples[{i}]: отсутствует поле '{field}'")

    # Проверка test_cases
    if "test_cases" in data:
        if not isinstance(data["test_cases"], list):
            errors.append("Поле 'test_cases' должно быть списком")
        elif not data["test_cases"]:
            errors.append("Поле 'test_cases' не должно быть пустым")
        else:
            for i, test in enumerate(data["test_cases"]):
                for field in REQUIRED_FIELDS["test_case"]:
                    if field not in test:
                        errors.append(f"test_cases[{i}]: отсутствует поле '{field}'")

    # Проверка языковых спецификаций
    has_language_spec = False
    for lang in ["python3", "go", "java", "javascript"]:
        if lang in data:
            has_language_spec = True
            lang_data = data[lang]

            for field in REQUIRED_FIELDS["language_spec"]:
                if field not in lang_data:
                    errors.append(f"{lang}: отсутствует поле '{field}'")

            # Проверка solutions
            if "solutions" in lang_data:
                if not isinstance(lang_data["solutions"], list):
                    errors.append(f"{lang}.solutions должен быть списком")
                elif not lang_data["solutions"]:
                    errors.append(f"{lang}.solutions не должен быть пустым")
                else:
                    for i, sol in enumerate(lang_data["solutions"]):
                        for field in REQUIRED_FIELDS["solution"]:
                            if field not in sol:
                                errors.append(f"{lang}.solutions[{i}]: отсутствует поле '{field}'")

    if not has_language_spec:
        errors.append("Отсутствует языковая спецификация (python3, go, java или javascript)")

    return errors


def validate_solution_code(task: Task, solution: Solution, language: str = "python3") -> SolutionValidationResult:
    """
    Проверяет одно каноническое решение на всех тестах.

    Args:
        task: Объект задачи.
        solution: Каноническое решение для проверки.
        language: Язык программирования.

    Returns:
        SolutionValidationResult с результатами.
    """
    try:
        result = validate_solution(
            code=solution.code,
            task=task,
            language=language,
            stop_on_first_failure=False
        )

        return SolutionValidationResult(
            solution_name=solution.name,
            passed=result.success,
            passed_tests=result.passed_tests,
            total_tests=result.total_tests
        )

    except Exception as e:
        return SolutionValidationResult(
            solution_name=solution.name,
            passed=False,
            passed_tests=0,
            total_tests=len(task.test_cases),
            error=str(e)
        )


def validate_solutions(task: Task, language: str = "python3") -> list[SolutionValidationResult]:
    """
    Проверяет все канонические решения задачи.

    Args:
        task: Объект задачи.
        language: Язык программирования.

    Returns:
        Список результатов для каждого решения.
    """
    solutions = task.get_solutions(language)
    results = []

    for solution in solutions:
        result = validate_solution_code(task, solution, language)
        results.append(result)

    return results


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
    """
    # Загружаем JSON
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ValidationResult(
            filepath=filepath,
            valid=False,
            schema_errors=[f"Невалидный JSON: {e}"]
        )
    except FileNotFoundError:
        return ValidationResult(
            filepath=filepath,
            valid=False,
            schema_errors=[f"Файл не найден: {filepath}"]
        )

    # Проверяем схему
    schema_errors = validate_task_schema(data)

    if schema_errors:
        return ValidationResult(
            filepath=filepath,
            valid=False,
            schema_errors=schema_errors
        )

    # Загружаем задачу
    try:
        task = load_task(filepath)
    except Exception as e:
        return ValidationResult(
            filepath=filepath,
            valid=False,
            schema_errors=[f"Ошибка загрузки задачи: {e}"]
        )

    # Проверяем решения
    solution_results = []
    if check_solutions:
        solution_results = validate_solutions(task)

    # Определяем общий статус валидности
    all_solutions_pass = all(r.passed for r in solution_results) if solution_results else True
    valid = len(schema_errors) == 0 and all_solutions_pass

    return ValidationResult(
        filepath=filepath,
        valid=valid,
        schema_errors=schema_errors,
        solution_results=solution_results
    )


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
    if not directory.exists():
        print(Colors.error(f"Директория не найдена: {directory}"))
        return []

    files = sorted(directory.glob("*.json"))
    results = []

    for filepath in files:
        result = validate_task_file(filepath, check_solutions)
        results.append(result)

    return results


def print_validation_report(results: list[ValidationResult]) -> None:
    """
    Выводит отчёт о валидации в консоль.
    """
    print(f"\n{Colors.bold('Валидация задач')}")
    print(DOUBLE_SEPARATOR)

    valid_count = 0

    for result in results:
        filename = result.filepath.name

        if result.valid:
            print(f"\n{Colors.success('✓')} {filename}")
            print("  Схема: OK")

            if result.solution_results:
                print("  Решения:")
                for sol in result.solution_results:
                    status = Colors.success('✓') if sol.passed else Colors.error('✗')
                    print(f"    {status} {sol.solution_name}: {sol.passed_tests}/{sol.total_tests} тестов")
                    if sol.error:
                        print(f"       {Colors.error(sol.error)}")

            valid_count += 1
        else:
            print(f"\n{Colors.error('✗')} {filename}")

            if result.schema_errors:
                print(f"  Схема: {len(result.schema_errors)} ошибок")
                for error in result.schema_errors:
                    print(f"    - {Colors.error(error)}")

            if result.solution_results:
                print("  Решения:")
                for sol in result.solution_results:
                    status = Colors.success('✓') if sol.passed else Colors.error('✗')
                    print(f"    {status} {sol.solution_name}: {sol.passed_tests}/{sol.total_tests} тестов")
                    if sol.error:
                        print(f"       {Colors.error(sol.error)}")

    print(f"\n{DOUBLE_SEPARATOR}")
    print(f"Итого: {valid_count}/{len(results)} задач валидны")

    if valid_count == len(results):
        print(Colors.success("\nВсе задачи прошли валидацию!"))
    else:
        print(Colors.error(f"\n{len(results) - valid_count} задач требуют исправления"))


def main():
    """CLI интерфейс для валидации."""
    parser = argparse.ArgumentParser(
        description="Валидация файлов задач LeetCode"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Путь к файлу задачи или директории"
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Проверять только схему JSON (без выполнения решений)"
    )

    args = parser.parse_args()

    path = args.path
    check_solutions = not args.schema_only

    if path.is_file():
        results = [validate_task_file(path, check_solutions)]
    elif path.is_dir():
        results = validate_all_tasks(path, check_solutions)
    else:
        print(Colors.error(f"Путь не найден: {path}"))
        sys.exit(1)

    print_validation_report(results)

    # Exit code
    if all(r.valid for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
