"""
Модуль отображения результатов.

Функции:
- report_results(execution_result) -> None
- format_test_result(test_result) -> str
- format_summary(execution_result) -> str
- format_error(test_result) -> str
"""

import json

from models import ExecutionResult, TestResult, TestStatus
from config import Colors, DOUBLE_SEPARATOR


def format_test_result(result: TestResult, verbose: bool = False) -> str:
    """
    Форматирует результат одного теста.

    Args:
        result: Результат теста.
        verbose: Показывать детали (input/output).

    Returns:
        Отформатированная строка.
    """
    time_str = f"({result.execution_time:.3f}s)"

    if result.status == TestStatus.PASSED:
        status_icon = Colors.success("✓")
        status_text = "passed"
    elif result.status == TestStatus.FAILED:
        status_icon = Colors.error("✗")
        status_text = "failed"
    elif result.status == TestStatus.ERROR:
        status_icon = Colors.error("✗")
        status_text = "error"
    elif result.status == TestStatus.TIMEOUT:
        status_icon = Colors.error("✗")
        status_text = "timeout"
    else:
        status_icon = "?"
        status_text = "unknown"

    line = f"{status_icon} Тест {result.test_number}/{result.total_tests}: {status_text} {time_str}"

    # Добавляем описание теста, если есть
    if result.description and verbose:
        line += f" - {Colors.muted(result.description)}"

    return line


def format_error_details(result: TestResult) -> str:
    """
    Форматирует детали ошибки.

    Args:
        result: Результат теста с ошибкой.

    Returns:
        Отформатированная строка с деталями.
    """
    lines = []

    # Описание теста
    if result.description:
        lines.append(f"  {Colors.muted(f'Тест: {result.description}')}")

    if result.status in (TestStatus.ERROR, TestStatus.TIMEOUT):
        # Runtime ошибка или таймаут
        lines.append(f"  {Colors.error(f'Error: {result.error_message}')}")
    else:
        # Wrong answer
        input_str = json.dumps(result.input_data, ensure_ascii=False)
        expected_str = json.dumps(result.expected, ensure_ascii=False)
        actual_str = json.dumps(result.actual, ensure_ascii=False)

        lines.append(f"  Input: {Colors.info(input_str)}")
        lines.append(f"  Expected: {Colors.success(expected_str)}")
        lines.append(f"  Actual: {Colors.error(actual_str)}")

    return "\n".join(lines)


def format_summary(result: ExecutionResult) -> str:
    """
    Форматирует итоговую сводку.

    Args:
        result: Полный результат выполнения.

    Returns:
        Отформатированная сводка.
    """
    lines = [DOUBLE_SEPARATOR]

    if result.success:
        lines.append(Colors.success("✓ Все тесты пройдены!"))
    else:
        lines.append(Colors.error(f"✗ Тесты не пройдены: {result.passed_tests}/{result.total_tests}"))

    lines.append(f"  Время выполнения: {result.total_time:.3f}s")
    lines.append(DOUBLE_SEPARATOR)

    return "\n".join(lines)


def report_results(result: ExecutionResult, verbose: bool = False) -> None:
    """
    Выводит полный отчёт о результатах.

    Args:
        result: Результат выполнения всех тестов.
        verbose: Показывать детали каждого теста.
    """
    print("\nПроверка решения...\n")

    for test_result in result.results:
        print(format_test_result(test_result, verbose))

        # Показываем детали для неуспешных тестов
        if test_result.status != TestStatus.PASSED:
            print(format_error_details(test_result))
            print()

    print(format_summary(result))
