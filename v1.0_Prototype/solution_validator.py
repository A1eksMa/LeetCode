"""
Модуль валидации пользовательских решений.

Функции:
- validate_solution(code, task) -> ExecutionResult
- run_single_test(code, function_name, test_case, test_number, arg_order) -> TestResult
- compare_results(actual, expected) -> bool
"""

from typing import Any
import time

from models import (
    Task, TestCase, TestResult, ExecutionResult, TestStatus
)
from executor import execute_code
from input_handler import parse_signature_args
from config import EXECUTION_TIMEOUT


def compare_results(actual: Any, expected: Any) -> bool:
    """
    Сравнивает фактический результат с ожидаемым.

    Args:
        actual: Результат выполнения пользовательского кода.
        expected: Ожидаемый результат из теста.

    Returns:
        True если результаты эквивалентны.
    """
    # Прямое сравнение
    if actual == expected:
        return True

    # Сравнение float с погрешностью
    if isinstance(actual, float) and isinstance(expected, float):
        return abs(actual - expected) < 1e-9

    # Сравнение списков float
    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            return False
        for a, e in zip(actual, expected):
            if isinstance(a, float) and isinstance(e, float):
                if abs(a - e) >= 1e-9:
                    return False
            elif a != e:
                return False
        return True

    return False


def run_single_test(
    code: str,
    function_name: str,
    test_case: TestCase,
    test_number: int,
    total_tests: int,
    arg_order: list[str],
    timeout: float = EXECUTION_TIMEOUT
) -> TestResult:
    """
    Выполняет один тест.

    Args:
        code: Пользовательский код.
        function_name: Имя функции.
        test_case: Тест-кейс с input и expected.
        test_number: Номер теста (для отчёта).
        total_tests: Общее количество тестов.
        arg_order: Порядок аргументов функции.
        timeout: Лимит времени.

    Returns:
        TestResult с результатом выполнения.
    """
    # Выполняем код
    exec_result = execute_code(
        code=code,
        function_name=function_name,
        args=test_case.input,
        arg_order=arg_order,
        timeout=timeout
    )

    # Обработка ошибок выполнения
    if not exec_result.success:
        if exec_result.error_type == "TimeoutError":
            status = TestStatus.TIMEOUT
        else:
            status = TestStatus.ERROR

        return TestResult(
            test_number=test_number,
            total_tests=total_tests,
            status=status,
            execution_time=exec_result.execution_time,
            input_data=test_case.input,
            expected=test_case.expected,
            actual=None,
            error_message=f"{exec_result.error_type}: {exec_result.error_message}",
            description=test_case.description
        )

    # Сравниваем результаты
    is_correct = compare_results(exec_result.result, test_case.expected)

    return TestResult(
        test_number=test_number,
        total_tests=total_tests,
        status=TestStatus.PASSED if is_correct else TestStatus.FAILED,
        execution_time=exec_result.execution_time,
        input_data=test_case.input,
        expected=test_case.expected,
        actual=exec_result.result,
        description=test_case.description
    )


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
    """
    # Получаем имя функции и порядок аргументов
    function_name = task.function_name
    signature = task.get_signature(language)
    arg_order = parse_signature_args(signature)

    if not function_name:
        return ExecutionResult(
            success=False,
            total_tests=0,
            passed_tests=0,
            total_time=0,
            results=[],
            error="Не удалось определить имя функции из сигнатуры"
        )

    results = []
    passed = 0
    total_time = 0
    total_tests = len(task.test_cases)

    start_time = time.perf_counter()

    for i, test_case in enumerate(task.test_cases, 1):
        result = run_single_test(
            code=code,
            function_name=function_name,
            test_case=test_case,
            test_number=i,
            total_tests=total_tests,
            arg_order=arg_order
        )

        results.append(result)
        total_time += result.execution_time

        if result.status == TestStatus.PASSED:
            passed += 1
        elif stop_on_first_failure:
            break

    total_time = time.perf_counter() - start_time

    return ExecutionResult(
        success=(passed == total_tests),
        total_tests=total_tests,
        passed_tests=passed,
        total_time=total_time,
        results=results
    )
