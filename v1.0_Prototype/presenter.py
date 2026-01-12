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
from config import Colors, SEPARATOR


def format_header(task: Task) -> str:
    """
    Форматирует заголовок задачи.

    Args:
        task: Объект задачи.

    Returns:
        Отформатированный заголовок.
    """
    difficulty_colors = {
        "easy": Colors.GREEN,
        "medium": Colors.YELLOW,
        "hard": Colors.RED
    }

    diff = task.difficulty.value
    color = difficulty_colors.get(diff, "")
    diff_str = f"{color}{diff}{Colors.RESET}"

    tags_str = ", ".join(task.tags)

    lines = [
        SEPARATOR,
        f"Задача #{task.id}: {Colors.bold(task.title)}",
        f"Сложность: {diff_str}",
        f"Теги: {tags_str}",
        SEPARATOR,
    ]

    return "\n".join(lines)


def format_description(description: str) -> str:
    """
    Форматирует описание задачи.

    Args:
        description: Текст описания.

    Returns:
        Отформатированный текст с переносами строк.
    """
    # Заменяем \n из JSON на реальные переносы строк
    return description.replace("\\n", "\n")


def format_example(example: Example, index: int) -> str:
    """
    Форматирует один пример.

    Args:
        example: Объект примера.
        index: Номер примера.

    Returns:
        Отформатированная строка примера.
    """
    lines = [f"\n{Colors.bold(f'Пример {index}:')}"]

    # Форматируем input
    input_parts = []
    for key, value in example.input.items():
        input_parts.append(f"{key} = {value}")
    lines.append(f"  Input: {', '.join(input_parts)}")

    # Output
    lines.append(f"  Output: {example.output}")

    # Explanation (если есть)
    if example.explanation:
        lines.append(f"  {Colors.muted('Пояснение: ' + example.explanation)}")

    return "\n".join(lines)


def format_examples(examples: list[Example]) -> str:
    """
    Форматирует все примеры задачи.

    Args:
        examples: Список примеров.

    Returns:
        Отформатированная строка со всеми примерами.
    """
    formatted = []
    for i, example in enumerate(examples, 1):
        formatted.append(format_example(example, i))

    return "\n".join(formatted)


def format_signature(task: Task, language: str = "python3") -> str:
    """
    Форматирует сигнатуру функции.

    Args:
        task: Объект задачи.
        language: Язык программирования.

    Returns:
        Отформатированная сигнатура.
    """
    signature = task.get_signature(language)
    if not signature:
        return ""

    return f"\n{Colors.bold('Сигнатура функции:')}\n  {Colors.info(signature)}"


def present_task(task: Task, language: str = "python3") -> None:
    """
    Выводит полное условие задачи в консоль.

    Args:
        task: Объект задачи.
        language: Язык программирования для сигнатуры.
    """
    print(format_header(task))
    print()
    print(format_description(task.description))
    print(format_examples(task.examples))
    print(format_signature(task, language))
    print()
    print(SEPARATOR)
