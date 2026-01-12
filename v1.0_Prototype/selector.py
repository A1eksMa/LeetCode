"""
Модуль выбора задачи из списка.

Функции:
- display_task_list(tasks) -> None
- get_user_choice(min_value, max_value) -> int
- select_task(tasks) -> Task
- select_random_task(tasks) -> Task
"""

import random

from models import Task
from config import Colors


def format_task_item(task: Task, index: int) -> str:
    """
    Форматирует одну строку списка задач.

    Args:
        task: Объект задачи.
        index: Номер в списке (для отображения).

    Returns:
        Отформатированная строка.
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

    return f"  [{index}] {task.title} ({diff_str}) [{tags_str}]"


def display_task_list(tasks: list[Task]) -> None:
    """
    Выводит список доступных задач.

    Args:
        tasks: Список задач для отображения.
    """
    print("\nДоступные задачи:")
    print(f"  [{Colors.info('0')}] Случайная задача")

    for i, task in enumerate(tasks, 1):
        print(format_task_item(task, i))

    print()


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
    while True:
        try:
            user_input = input(f"{prompt} ({min_value}-{max_value}): ").strip()
            value = int(user_input)

            if min_value <= value <= max_value:
                return value
            else:
                print(Colors.error(f"Введите число от {min_value} до {max_value}"))
        except ValueError:
            print(Colors.error("Введите число"))


def select_random_task(tasks: list[Task]) -> Task:
    """
    Выбирает случайную задачу из списка.

    Args:
        tasks: Список задач.

    Returns:
        Случайно выбранная задача.
    """
    return random.choice(tasks)


def select_task(tasks: list[Task]) -> Task:
    """
    Полный flow выбора задачи: показывает список, получает выбор.

    Args:
        tasks: Список доступных задач.

    Returns:
        Выбранная задача (или случайная, если выбран 0).
    """
    display_task_list(tasks)

    choice = get_user_choice(0, len(tasks))

    if choice == 0:
        task = select_random_task(tasks)
        print(f"\nВыбрана случайная задача: {Colors.bold(task.title)}")
        return task

    return tasks[choice - 1]
