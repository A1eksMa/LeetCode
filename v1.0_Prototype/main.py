#!/usr/bin/env python3
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

from config import TASKS_DIR, DEFAULT_LANGUAGE, Colors, DOUBLE_SEPARATOR
from task_loader import load_all_tasks
from selector import select_task
from presenter import present_task
from input_handler import (
    read_user_code, read_code_from_file, validate_code_syntax
)
from solution_validator import validate_solution
from result_reporter import report_results


def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки.

    Returns:
        Объект с аргументами: task, file, verbose.
    """
    parser = argparse.ArgumentParser(
        description="LeetCode Practice CLI - решайте алгоритмические задачи",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main.py                    Интерактивный режим
  python main.py --task 2           Перейти сразу к задаче #2
  python main.py --task 1 --file solution.py   Проверить решение из файла
  python main.py --verbose          Подробный вывод
        """
    )

    parser.add_argument(
        "--task", "-t",
        type=int,
        help="Номер задачи (пропустить меню выбора)"
    )
    parser.add_argument(
        "--file", "-f",
        type=Path,
        help="Файл с решением"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод результатов"
    )

    return parser.parse_args()


def display_welcome() -> None:
    """
    Выводит приветственный баннер.
    """
    banner = f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║       LeetCode Practice CLI            ║
╚════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def ask_continue() -> bool:
    """
    Спрашивает пользователя о продолжении.

    Returns:
        True если пользователь хочет продолжить.
    """
    while True:
        answer = input("\nПродолжить? (y/n): ").strip().lower()
        if answer in ("y", "yes", "д", "да", ""):
            return True
        if answer in ("n", "no", "н", "нет"):
            return False
        print("Введите y или n")


def run_solve_flow(
    task,
    code: str | None = None,
    verbose: bool = False,
    language: str = DEFAULT_LANGUAGE
) -> bool:
    """
    Выполняет полный flow решения одной задачи.

    Args:
        task: Задача для решения.
        code: Код решения (если None, запрашивается у пользователя).
        verbose: Подробный вывод.
        language: Язык программирования.

    Returns:
        True если все тесты пройдены.
    """
    # Показываем условие задачи
    present_task(task, language)

    previous_code = None

    while True:
        # Получаем код
        if code is None:
            result = read_user_code(task, previous_code, language)

            if result.cancelled:
                print(Colors.warning("\nОтменено."))
                return False

            user_code = result.code
        else:
            user_code = code

        # Проверяем синтаксис
        is_valid, error_msg = validate_code_syntax(user_code)

        if not is_valid:
            print(f"\n{Colors.error('✗ Синтаксическая ошибка:')}")
            print(f"  {error_msg}")
            print(Colors.warning("\nПопробуйте ещё раз."))

            if code is not None:
                # Если код из файла — выходим
                return False

            previous_code = user_code
            continue

        # Валидируем решение
        exec_result = validate_solution(user_code, task, language)

        # Выводим результаты
        report_results(exec_result, verbose)

        if exec_result.success:
            return True

        if code is not None:
            # Если код из файла — выходим после одной попытки
            return False

        # Спрашиваем о повторной попытке
        retry = input("\nПопробовать ещё раз? (y/n): ").strip().lower()
        if retry not in ("y", "yes", "д", "да", ""):
            return False

        previous_code = user_code


def main_loop(tasks: list, verbose: bool = False) -> None:
    """
    Главный цикл приложения.

    Args:
        tasks: Список доступных задач.
        verbose: Подробный вывод.
    """
    while True:
        try:
            # Выбор задачи
            task = select_task(tasks)

            # Решение задачи
            run_solve_flow(task, verbose=verbose)

            # Продолжить?
            if not ask_continue():
                break

        except KeyboardInterrupt:
            print("\n")
            break

    print(Colors.info("\nДо свидания!"))


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
        print(Colors.error(f"Ошибка: директория {TASKS_DIR} не найдена"))
        return 1

    if not tasks:
        print(Colors.error("Ошибка: задачи не найдены"))
        print(f"Добавьте JSON-файлы задач в директорию: {TASKS_DIR}")
        return 1

    display_welcome()

    # Режим с указанным файлом решения
    if args.file:
        try:
            code = read_code_from_file(args.file)
        except FileNotFoundError:
            print(Colors.error(f"Файл не найден: {args.file}"))
            return 1

        if args.task:
            if args.task < 1 or args.task > len(tasks):
                print(Colors.error(f"Задача #{args.task} не найдена"))
                return 1
            task = tasks[args.task - 1]
        else:
            task = select_task(tasks)

        success = run_solve_flow(task, code, args.verbose)
        return 0 if success else 1

    # Режим с указанной задачей (без файла)
    if args.task:
        if args.task < 1 or args.task > len(tasks):
            print(Colors.error(f"Задача #{args.task} не найдена"))
            return 1
        task = tasks[args.task - 1]
        success = run_solve_flow(task, verbose=args.verbose)
        return 0 if success else 1

    # Интерактивный режим
    try:
        main_loop(tasks, args.verbose)
    except KeyboardInterrupt:
        print(Colors.info("\n\nДо свидания!"))

    return 0


if __name__ == "__main__":
    # Для корректной работы multiprocessing на всех платформах
    import multiprocessing as mp
    mp.set_start_method("spawn", force=True)

    sys.exit(main())
