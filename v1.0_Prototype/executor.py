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
import time
import copy
from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionOutput:
    """Результат выполнения кода."""
    success: bool
    result: Any | None = None
    error_type: str | None = None
    error_message: str | None = None
    execution_time: float = 0.0


# Безопасные built-in функции для sandbox
SAFE_BUILTINS = {
    # Типы
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "frozenset": frozenset,
    "bytes": bytes,
    "bytearray": bytearray,

    # Функции для коллекций
    "len": len,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "reversed": reversed,
    "sorted": sorted,

    # Математические функции
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "round": round,
    "divmod": divmod,

    # Логические функции
    "all": all,
    "any": any,

    # Преобразования
    "chr": chr,
    "ord": ord,
    "hex": hex,
    "bin": bin,
    "oct": oct,

    # Прочее
    "isinstance": isinstance,
    "issubclass": issubclass,
    "hasattr": hasattr,
    "getattr": getattr,
    "setattr": setattr,
    "callable": callable,
    "iter": iter,
    "next": next,
    "slice": slice,
    "repr": repr,
    "hash": hash,
    "id": id,
    "type": type,
    "object": object,
    "property": property,
    "staticmethod": staticmethod,
    "classmethod": classmethod,
    "super": super,

    # None, True, False
    "None": None,
    "True": True,
    "False": False,

    # Исключения (для перехвата)
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "AttributeError": AttributeError,
    "ZeroDivisionError": ZeroDivisionError,
    "StopIteration": StopIteration,
}


def create_sandbox_globals() -> dict:
    """
    Создаёт ограниченное глобальное окружение для exec().

    Returns:
        Словарь с безопасным набором built-in функций.
    """
    return {
        "__builtins__": SAFE_BUILTINS,
        "__name__": "__main__",
    }


def prepare_arguments(test_input: dict[str, Any]) -> dict[str, Any]:
    """
    Подготавливает аргументы для вызова функции.

    Args:
        test_input: Входные данные теста.

    Returns:
        Словарь аргументов (глубокая копия для изоляции).
    """
    return copy.deepcopy(test_input)


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
    """
    try:
        # Создаём sandbox окружение
        sandbox_globals = create_sandbox_globals()
        sandbox_locals = {}

        # Выполняем код пользователя
        exec(code, sandbox_globals, sandbox_locals)

        # Получаем функцию
        if function_name not in sandbox_locals:
            result_queue.put({
                "success": False,
                "error_type": "NameError",
                "error_message": f"Функция '{function_name}' не определена"
            })
            return

        func = sandbox_locals[function_name]

        # Подготавливаем аргументы в правильном порядке
        ordered_args = [args[name] for name in arg_order if name in args]

        # Вызываем функцию
        start_time = time.perf_counter()
        result = func(*ordered_args)
        execution_time = time.perf_counter() - start_time

        result_queue.put({
            "success": True,
            "result": result,
            "execution_time": execution_time
        })

    except Exception as e:
        result_queue.put({
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e)
        })


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
    """
    # Подготавливаем аргументы (глубокая копия)
    safe_args = prepare_arguments(args)

    # Создаём очередь для результата
    result_queue = mp.Queue()

    # Создаём и запускаем процесс
    process = mp.Process(
        target=run_in_process,
        args=(code, function_name, safe_args, arg_order, result_queue)
    )

    start_time = time.perf_counter()
    process.start()

    # Ждём завершения с таймаутом
    process.join(timeout=timeout)

    if process.is_alive():
        # Таймаут — убиваем процесс
        process.terminate()
        process.join(timeout=1)

        # Если всё ещё жив — kill
        if process.is_alive():
            process.kill()
            process.join()

        return ExecutionOutput(
            success=False,
            error_type="TimeoutError",
            error_message=f"Превышен лимит времени ({timeout} сек)",
            execution_time=timeout
        )

    # Получаем результат из очереди
    try:
        result_data = result_queue.get_nowait()
    except Exception:
        return ExecutionOutput(
            success=False,
            error_type="InternalError",
            error_message="Не удалось получить результат выполнения"
        )

    total_time = time.perf_counter() - start_time

    if result_data.get("success"):
        return ExecutionOutput(
            success=True,
            result=result_data.get("result"),
            execution_time=result_data.get("execution_time", total_time)
        )
    else:
        return ExecutionOutput(
            success=False,
            error_type=result_data.get("error_type"),
            error_message=result_data.get("error_message"),
            execution_time=total_time
        )
