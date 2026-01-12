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

import ast
import re
from pathlib import Path

from models import Task, InputResult
from config import Colors, SEPARATOR


def validate_code_syntax(code: str) -> tuple[bool, str | None]:
    """
    Проверяет синтаксическую корректность кода.

    Args:
        code: Python-код для проверки.

    Returns:
        Кортеж (is_valid, error_message).
        Если код валиден: (True, None)
        Если невалиден: (False, "SyntaxError: ...")
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        error_msg = f"SyntaxError: {e.msg} (строка {e.lineno})"
        return False, error_msg


def extract_function_name(code: str) -> str | None:
    """
    Извлекает имя определённой функции из кода.

    Args:
        code: Python-код.

    Returns:
        Имя первой определённой функции или None.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node.name
    except SyntaxError:
        pass
    return None


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
    """
    # Извлекаем содержимое скобок
    match = re.search(r'\(([^)]*)\)', signature)
    if not match:
        return []

    args_str = match.group(1)
    if not args_str.strip():
        return []

    args = []
    # Разбиваем по запятым, учитывая вложенные скобки
    depth = 0
    current = []

    for char in args_str:
        if char in '([{':
            depth += 1
            current.append(char)
        elif char in ')]}':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            args.append(''.join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        args.append(''.join(current).strip())

    # Извлекаем имена аргументов (до : или =)
    arg_names = []
    for arg in args:
        arg = arg.strip()
        if not arg:
            continue
        # Убираем аннотацию типа и значение по умолчанию
        name = re.split(r'[:\s=]', arg)[0].strip()
        if name and name != 'self':
            arg_names.append(name)

    return arg_names


def show_hint(task: Task, hint_index: int, language: str = "python3") -> int:
    """
    Показывает подсказку (каноническое решение) пользователю.

    Args:
        task: Текущая задача.
        hint_index: Индекс текущей подсказки (0, 1, 2...).
        language: Язык программирования.

    Returns:
        Новый hint_index (для следующей подсказки).
    """
    solutions = task.get_solutions(language)

    if not solutions:
        print(Colors.warning("\nПодсказки для этой задачи недоступны.\n"))
        return hint_index

    if hint_index >= len(solutions):
        print(Colors.warning("\nБольше подсказок нет.\n"))
        return hint_index

    solution = solutions[hint_index]

    print(f"\n{Colors.warning('═' * 40)}")
    print(Colors.warning(f"Подсказка {hint_index + 1}/{len(solutions)}: {solution.name}"))
    print(Colors.muted(f"Сложность: {solution.complexity}"))
    print(Colors.warning('─' * 40))
    print(Colors.info(solution.code))
    print(Colors.warning('═' * 40))
    print()

    return hint_index + 1


def show_previous_code(code: str) -> None:
    """
    Показывает предыдущий код пользователя.

    Args:
        code: Предыдущий код.
    """
    print(Colors.muted("\nПредыдущий код (введите новый или исправьте):"))
    print(Colors.muted("┌" + "─" * 38))
    for line in code.split("\n"):
        print(Colors.muted(f"│ {line}"))
    print(Colors.muted("└" + "─" * 38))
    print()


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
    """
    hint_index = 0

    # Показываем предыдущий код, если есть
    if previous_code:
        show_previous_code(previous_code)

    print("Введите решение (двойной Enter для завершения, !hint для подсказки):")

    lines = []
    empty_count = 0

    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break

        # Проверка специальных команд
        stripped = line.strip().lower()

        if stripped == "!hint":
            hint_index = show_hint(task, hint_index, language)
            continue

        if stripped == "!reset":
            lines = []
            empty_count = 0
            print(Colors.info("Код очищен. Введите заново:"))
            continue

        if stripped == "!cancel":
            return InputResult(code=None, cancelled=True)

        # Обработка пустых строк
        if not line.strip():
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append("")
        else:
            empty_count = 0
            lines.append(line)

    # Удаляем trailing пустые строки
    while lines and not lines[-1].strip():
        lines.pop()

    code = "\n".join(lines)

    if not code.strip():
        return InputResult(code=None, cancelled=True)

    return InputResult(code=code)


def read_code_from_file(filepath: Path) -> str:
    """
    Читает код из файла.

    Args:
        filepath: Путь к файлу с кодом.

    Returns:
        Содержимое файла.

    Raises:
        FileNotFoundError: Файл не найден.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
