# LeetCode Practice Bot

Telegram-бот для практики алгоритмических задач в стиле LeetCode. Проект развивается поэтапно: от CLI-прототипа до полноценного Telegram-бота с базой данных.

## Текущий этап: Прототип (CLI)

Минимальный работающий продукт — консольное приложение для решения алгоритмических задач.

## Быстрый старт

```bash
# Перейти в директорию прототипа
cd prototype

# Запустить приложение
python main.py
```

## Возможности

- Выбор задачи из списка или случайная задача
- Просмотр условия, примеров и сигнатуры функции
- Ввод решения прямо в терминале
- Автоматическая проверка на тестах
- Подсказки с каноническими решениями (`!hint`)
- Редактирование кода после ошибки
- Валидатор JSON-файлов задач

## Использование

### Интерактивный режим

```bash
python main.py
```

```
╔════════════════════════════════════════╗
║       LeetCode Practice CLI            ║
╚════════════════════════════════════════╝

Доступные задачи:
  [0] Случайная задача
  [1] Two Sum (easy) [array, hash-table]
  [2] Reverse String (easy) [string, two-pointers]
  [3] Valid Palindrome (easy) [string, two-pointers]

Выберите задачу (0-3): 1

────────────────────────────────────────
Задача #1: Two Sum
Сложность: easy
Теги: array, hash-table
────────────────────────────────────────

Дан массив целых чисел nums и целое число target...

Сигнатура функции:
  def two_sum(nums: list[int], target: int) -> list[int]:

────────────────────────────────────────

Введите решение (двойной Enter для завершения, !hint для подсказки):
>>> def two_sum(nums, target):
>>>     seen = {}
>>>     for i, num in enumerate(nums):
>>>         if target - num in seen:
>>>             return [seen[target - num], i]
>>>         seen[num] = i
>>>     return []
>>>
>>>

Проверка решения...

✓ Тест 1/7: passed (0.001s)
✓ Тест 2/7: passed (0.001s)
✓ Тест 3/7: passed (0.001s)
✓ Тест 4/7: passed (0.001s)
✓ Тест 5/7: passed (0.001s)
✓ Тест 6/7: passed (0.001s)
✓ Тест 7/7: passed (0.001s)

════════════════════════════════════════
✓ Все тесты пройдены!
  Время выполнения: 0.015s
════════════════════════════════════════
```

### Параметры командной строки

```bash
# Сразу перейти к задаче #2
python main.py --task 2

# Проверить решение из файла
python main.py --task 1 --file solution.py

# Подробный вывод результатов
python main.py --verbose

# Справка
python main.py --help
```

### Специальные команды во время ввода кода

| Команда   | Описание |
|-----------|----------|
| `!hint`   | Показать каноническое решение |
| `!reset`  | Очистить введённый код |
| `!cancel` | Отменить и вернуться к выбору задачи |

Ввод кода завершается **двойным Enter** (две пустые строки подряд).

## Валидатор задач

Проверяет JSON-файлы задач на корректность схемы и работоспособность канонических решений.

```bash
# Проверить одну задачу
python task_validator.py tasks/1_two_sum.json

# Проверить все задачи в директории
python task_validator.py tasks/

# Проверить только схему (без выполнения решений)
python task_validator.py --schema-only tasks/
```

Пример вывода:

```
Валидация задач
════════════════════════════════════════

✓ 1_two_sum.json
  Схема: OK
  Решения:
    ✓ Brute Force: 7/7 тестов
    ✓ Hash Map (один проход): 7/7 тестов
    ✓ Hash Map (два прохода): 7/7 тестов

════════════════════════════════════════
Итого: 3/3 задач валидны
```

## Структура проекта

```
LeetCode/
├── README.md                 # Этот файл
├── proposals/                # Документация и планы
│   ├── functional_requirements.md
│   ├── technical_requirements.md
│   ├── roadmap.md
│   └── stage1_technical_spec.md
└── prototype/                # CLI-прототип
    ├── main.py               # Точка входа
    ├── config.py             # Конфигурация
    ├── models.py             # Модели данных
    ├── task_loader.py        # Загрузка задач из JSON
    ├── task_validator.py     # Валидация JSON-файлов
    ├── selector.py           # Выбор задачи
    ├── presenter.py          # Отображение условия
    ├── input_handler.py      # Ввод кода пользователя
    ├── executor.py           # Выполнение кода (sandbox)
    ├── solution_validator.py # Проверка решений
    ├── result_reporter.py    # Вывод результатов
    └── tasks/                # JSON-файлы задач
        ├── 1_two_sum.json
        ├── 2_reverse_string.json
        └── 3_valid_palindrome.json
```

## Формат JSON-файла задачи

```json
{
  "id": 1,
  "title": "Two Sum",
  "difficulty": "easy",
  "tags": ["array", "hash-table"],
  "description": "Описание задачи...",
  "examples": [
    {
      "input": {"nums": [2, 7, 11, 15], "target": 9},
      "output": [0, 1],
      "explanation": "Пояснение"
    }
  ],
  "test_cases": [
    {
      "input": {"nums": [2, 7, 11, 15], "target": 9},
      "expected": [0, 1],
      "description": "базовый случай"
    }
  ],
  "python3": {
    "function_signature": "def two_sum(nums: list[int], target: int) -> list[int]:",
    "solutions": [
      {
        "name": "Hash Map",
        "complexity": "O(n)",
        "code": "def two_sum(nums, target):\n    ..."
      }
    ]
  }
}
```

## Добавление новой задачи

1. Создайте JSON-файл в `prototype/tasks/` по шаблону выше
2. Именование: `{номер}_{slug}.json` (например, `4_merge_sorted.json`)
3. Запустите валидатор для проверки:
   ```bash
   python task_validator.py tasks/4_merge_sorted.json
   ```

## Требования

- Python 3.9+
- Стандартная библиотека (без внешних зависимостей)

## Roadmap

| Этап | Описание | Статус |
|------|----------|--------|
| 1. Прототип | CLI-приложение, JSON-файлы | **В работе** |
| 2. Развитие | Telegram-бот, SQLite, фильтры | Планируется |
| 3. Зрелость | PostgreSQL, Docker, CI/CD | Планируется |

Подробнее: [proposals/roadmap.md](proposals/roadmap.md)

## Безопасность выполнения кода

- Код выполняется в отдельном процессе (`multiprocessing`)
- Ограниченный набор built-in функций (sandbox)
- Таймаут на выполнение (по умолчанию 5 сек)
- Принудительное завершение зависших процессов

## Лицензия

MIT
