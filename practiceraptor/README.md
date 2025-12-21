# PracticeRaptor

Telegram-бот для практики алгоритмических задач в стиле LeetCode. Проект развивается поэтапно: от CLI-прототипа до полноценного Telegram-бота с базой данных.

## Текущий этап: Stage 1.5 — Выделение ядра (Core Extraction)

Этот этап включает рефакторинг существующего CLI-прототипа в архитектуру Hexagonal (Ports & Adapters) с выделением независимого ядра. Вся бизнес-логика отделена от инфраструктуры, а зависимости инвертированы с помощью простой системы Dependency Injection. Функциональность CLI остается **идентичной** прототипу, но реализована на новой, более гибкой архитектуре.

### Основные изменения и возможности:

*   **Hexagonal Architecture (Ports & Adapters):** Проект теперь строго разделен на ядро (Core), порты (Ports) и адаптеры (Adapters).
    *   **Core:** Содержит доменные модели (неизменяемые dataclasses с поддержкой i18n), перечисления, типы ошибок и чистые сервисные функции для бизнес-логики.
    *   **Ports:** Определены как интерфейсы `typing.Protocol` для репозиториев (хранение данных), исполнителей кода и провайдеров аутентификации.
    *   **Adapters:** Реализации этих портов, включая JSON-репозитории для хранения данных, `LocalExecutor` для безопасного выполнения кода в песочнице с использованием `multiprocessing` и `AnonymousAuthProvider` для CLI.
*   **Dependency Injection (DI):** Внедрена система Dependency Injection с использованием неизменяемого контейнера (`Container`) и загрузкой конфигурации из YAML-файлов. Это позволяет легко менять реализации адаптеров без изменения кода ядра.
*   **Расширенные модели данных:** Все доменные модели (Problem, User, Draft, Submission, Progress и т.д.) определены как неизменяемые `dataclasses`, что повышает предсказуемость состояния.
*   **Интернационализация (i18n):** Введена поддержка `LocalizedText` для многоязычных описаний и заголовков задач.
*   **Улучшенная обработка ошибок:** Использование типа `Result` (`Ok`/`Err`) для явной обработки успешных результатов и ошибок в функциональном стиле.
*   **Рефакторинг CLI:** Клиент командной строки переработан как "тонкий клиент", который взаимодействует с ядром через DI-контейнер, сохраняя при этом привычный пользовательский интерфейс и все возможности прототипа.

## Как запустить

```bash
  # Убедитесь, что вы находитесь в корневой директории проекта (PracticeRaptor)
  # cd /root/github/PracticeRaptor

  # Интерактивный режим (выбор задачи из списка)
  python3 -m practiceraptor.clients.cli.main

  # Конкретная задача по ID
  python3 -m practiceraptor.clients.cli.main --task 1

  # Решение из файла
  python3 -m practiceraptor.clients.cli.main --task 1 --file solution.py

  # Подробный вывод результатов (verbose)
  python3 -m practiceraptor.clients.cli.main --task 1 --verbose

  # Справка
  python3 -m practiceraptor.clients.cli.main --help
```

## Возможности CLI (идентично прототипу)

*   Выбор задачи из списка или случайная задача.
*   Просмотр условия, примеров и сигнатуры функции.
*   Ввод решения прямо в терминале.
*   Автоматическая проверка на тестах.
*   Подсказки с каноническими решениями (`!hint`).
*   Редактирование кода после ошибки.
*   Валидатор JSON-файлов задач (теперь часть архитектуры, не отдельный скрипт).

### Специальные команды во время ввода кода

| Команда   | Описание                            |
|-----------|-------------------------------------|
| `!hint`   | Показать каноническое решение       |
| `!reset`  | Очистить введённый код              |
| `!cancel` | Отменить и вернуться к выбору задачи |

Ввод кода завершается **двойным Enter** (две пустые строки подряд).

## Архитектурные решения

### Hexagonal Architecture (Ports & Adapters)

  ┌─────────────────────────────────────────────────────────────┐
  │                         CLIENTS                              │
  │         CLI │ Telegram │ Web │ Widget                        │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                      CORE (ядро)                             │
  │                                                              │
  │   Работает через интерфейсы (Ports):                         │
  │   • IProblemRepository (чтение задач)                        │
  │   • IUserRepository (управление пользователями)              │
  │   • IDraftRepository (черновики кода)                        │
  │   • ISubmissionRepository (решения пользователей)            │
  │   • IProgressRepository (прогресс пользователя по задачам)   │
  │   • ICodeExecutor (выполнение кода)                          │
  │   • IAuthProvider (аутентификация)                           │
  └──────────────────────────┬──────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   STORAGE   │    │  EXECUTOR   │    │    AUTH     │
  │ JSON        │    │ Local       │    │ Anonymous   │
  │ SQLite      │    │ Docker      │    │ Telegram    │
  │ PostgreSQL  │    │ Remote API  │    │ Token/OAuth │
  └─────────────┘    └─────────────┘    └─────────────┘

### Примеры конфигураций

Гибкая система конфигурации позволяет легко переключать адаптеры.

  Разработка / CLI:
  storage: json
  executor: local
  auth: anonymous

  Конфигурация интрефейса командной строки загружается из `config/config.yaml` (или `config/config.test.yaml` для тестов).

  Telegram на VPS (планируется):
  storage: postgresql
  executor: docker
  auth: telegram

  Экзотическая комбинация (планируется):
  storage: json           # файлы локально
  executor: remote        # сервис на другом сервере
    url: http://executor.example.com:8080
  auth: telegram

### Текущее состояние компонентов (Stage 1.5)

| Компонент   | Реализовано                          | Планируется (будущие этапы)            |
|-------------|--------------------------------------|----------------------------------------|
| **Storage** | JSON-репозитории                     | SQLite, PostgreSQL (Stage 1.7)         |
| **Executor**| Local (на основе `multiprocessing`)  | Docker, Remote API (Stage 1.8)         |
| **Auth**    | Anonymous (для локального CLI)       | Telegram, Token/OAuth (Stage 2+)       |
| **Clients** | CLI (обновленный и рефакторизованный) | Telegram Bot (Stage 2), Web UI (Stage 3)|

## Структура проекта (после Stage 1.5)

```
PracticeRaptor/
├── practiceraptor/               # Основной код приложения
│   ├── core/                     # Ядро приложения (независимо от инфраструктуры)
│   │   ├── domain/               # Доменные модели, перечисления, ошибки, Result type
│   │   │   ├── enums.py          # Перечисления (Difficulty, Language, ProgressStatus и т.д.)
│   │   │   ├── errors.py         # Доменные ошибки (NotFoundError, ExecutionError и т.д.)
│   │   │   ├── models.py         # Неизменяемые dataclasses для всех сущностей (Problem, User, Draft, etc.)
│   │   │   ├── factories.py      # Фабричные функции для создания доменных объектов
│   │   │   └── result.py         # Тип Result (Ok/Err) для функциональной обработки ошибок
│   │   ├── ports/                # Интерфейсы (Ports) для внешних зависимостей (Protocol)
│   │   │   ├── auth.py           # IAuthProvider
│   │   │   ├── executors.py      # ICodeExecutor
│   │   │   └── repositories.py   # IProblemRepository, IUserRepository, etc.
│   │   └── services/             # Чистые функции бизнес-логики (используют Ports)
│   │       ├── drafts.py         # Управление черновиками кода
│   │       ├── execution.py      # Выполнение и валидация кода
│   │       ├── problems.py       # Получение, фильтрация и отображение задач
│   │       └── progress.py       # Отслеживание прогресса пользователя
│   │
│   ├── adapters/                 # Адаптеры (реализации Ports)
│   │   ├── auth/                 # Адаптеры аутентификации
│   │   │   └── anonymous_auth.py # Анонимный провайдер (для CLI)
│   │   ├── executors/            # Адаптеры выполнения кода
│   │   │   └── local_executor.py # Локальный исполнитель кода (песочница на multiprocessing)
│   │   └── storage/              # Адаптеры хранения данных (репозитории)
│   │       ├── json_base.py          # Базовый класс для JSON-хранилища
│   │       ├── json_draft_repository.py
│   │       ├── json_problem_repository.py
│   │       ├── json_progress_repository.py
│   │       ├── json_submission_repository.py
│   │       └── json_user_repository.py
│   │
│   ├── clients/                  # Клиенты приложения
│   │   └── cli/                  # Клиент командной строки
│   │       ├── app.py            # Главный класс CLI-приложения
│   │       ├── colors.py         # ANSI-коды для цветного вывода
│   │       ├── input_handler.py  # Обработка пользовательского ввода
│   │       └── main.py           # Точка входа CLI, парсинг аргументов
│   │
│   ├── config/                   # Файлы конфигурации
│   │   ├── config.example.yaml   # Пример конфигурации
│   │   ├── config.test.yaml      # Конфигурация для тестового окружения
│   │   └── config.yaml           # Рабочая конфигурация
│   │
│   ├── data/                     # Директории для хранения данных
│   │   └── problems/             # JSON-файлы с задачами
│   │
│   └── di/                       # Dependency Injection
│       ├── config.py             # Модели конфигурации и загрузчик YAML
│       ├── container.py          # Неизменяемый DI-контейнер
│       └── providers.py          # Фабрики для создания зависимостей
│
├── tests/                        # Тесты (Unit, Integration, E2E)
│   ├── unit/                     # Быстрые, изолированные тесты
│   ├── integration/              # Тесты взаимодействия компонентов
│   ├── fixtures/                 # Общие фикстуры и фабрики тестовых данных
│   └── conftest.py               # Конфигурация pytest и общие фикстуры
│
├── docker/                       # Конфигурация Docker
│   ├── Dockerfile.test           # Dockerfile для тестового окружения
│   └── docker-compose.test.yml   # Docker Compose для запуска тестов
│
├── .github/                      # Конфигурация GitHub
│   └── workflows/                # GitHub Actions CI
│       └── test.yml              # CI пайплайн
│
├── .gitignore                    # Игнорируемые файлы Git
├── pyproject.toml                # Метаданные проекта и инструменты (ruff, mypy, pytest)
└── LICENSE                       # Лицензия проекта
```

## Формат JSON-файла задачи (обновленный с i18n)

```json
{
  "id": 1,
  "title": {
    "en": "Two Sum",
    "ru": "Сумма двух чисел"
  },
  "description": {
    "en": "Given an array of integers nums and an integer target...",
    "ru": "Дан массив целых чисел nums и целое число target..."
  },
  "difficulty": "easy",
  "tags": ["array", "hash-table"],
  "examples": [
    {
      "input": {"nums": [2, 7, 11, 15], "target": 9},
      "output": [0, 1],
      "explanation": {"en": "nums[0] + nums[1] = 9", "ru": "nums[0] + nums[1] = 9"}
    }
  ],
  "test_cases": [
    {
      "input": {"nums": [2, 7, 11, 15], "target": 9},
      "expected": [0, 1],
      "description": "базовый случай",
      "is_hidden": false
    }
  ],
  "languages": {
    "python3": {
      "function_signature": "def two_sum(nums: list[int], target: int) -> list[int]:",
      "solutions": [
        {
          "name": "Hash Map",
          "complexity": "O(n)",
          "code": "def two_sum(nums, target):\n    ..."
        }
      ]
    },
    "go": {
      "function_signature": "func twoSum(nums []int, target int) []int {",
      "solutions": []
    }
  },
  "hints": [
    {"en": "Consider using a hash map.", "ru": "Рассмотрите использование хеш-таблицы."}
  ]
}
```
`JsonProblemRepository` обратно совместим со старым форматом JSON из прототипа.

## Добавление новой задачи

1.  Создайте JSON-файл в `practiceraptor/data/problems/` по шаблону выше.
2.  Именование: `{номер}_{slug}.json` (например, `4_merge_sorted.json`).
3.  Убедитесь, что формат JSON соответствует новым требованиям (особенно для i18n).
4.  Валидация JSON-файлов задач теперь происходит внутри приложения.

## Тестирование

Проект обладает всесторонним тестовым покрытием:
*   **Unit-тесты:** Быстрые и изолированные тесты для каждого модуля.
*   **Integration-тесты:** Проверяют взаимодействие между несколькими компонентами (например, сервисы и репозитории).
*   **Code Coverage:** Не менее 80% покрытия кода.
*   **Static Analysis:** Используется `mypy` для статической проверки типов и `ruff` для форматирования и линтинга.
*   **Docker-окружение:** Тесты могут быть запущены в изолированном Docker-контейнере для обеспечения воспроизводимости.
*   **CI/CD:** Настроен GitHub Actions для автоматического запуска тестов, линтеров и проверки покрытия при каждом push и pull request.

### Запуск тестов

```bash
# Локально (предполагается активация виртуального окружения)
pytest                              # Все тесты
pytest tests/unit                   # Только unit-тесты
pytest tests/integration            # Только интеграционные тесты
pytest -v --tb=long                 # Подробный вывод с полным traceback
pytest --cov --cov-report=html      # С отчетом о покрытии (генерирует htmlcov/)

# В Docker (для изолированного запуска)
docker-compose -f docker/docker-compose.test.yml up --build

# Проверка линтерами и статическим анализом
ruff check .
mypy practiceraptor/core practiceraptor/adapters practiceraptor/di practiceraptor/clients
```

## Требования

*   Python 3.11+
*   Зависимости из `pyproject.toml` (устанавливаются `pip install -e .[dev]`)

## Roadmap

| Этап | Описание                                             | Статус      |
|------|------------------------------------------------------|-------------|
| 1.0  | Прототип CLI-приложения                              | Завершен    |
| 1.5  | Выделение ядра (Hexagonal Architecture, DI, тесты)   | **Завершен**|
| 1.6  | Улучшение CLI (User-специфичные функции, прогресс) | Планируется |
| 1.7  | Адаптер SQLite, сохранение прогресса                 | Планируется |
| 1.8  | Адаптер Docker Executor, Телеграм-аутентификация     | Планируется |
| 2.0  | Telegram-бот, расширенная функциональность           | Планируется |
| 3.0  | Веб-интерфейс, облачные сервисы                      | Планируется |

Подробнее: [proposals/roadmap.md](proposals/roadmap.md)

## Безопасность выполнения кода

*   Код пользователя выполняется в отдельном процессе (`multiprocessing`).
*   Ограниченный набор встроенных функций Python (`SAFE_BUILTINS`) в песочнице.
*   Таймаут на выполнение (по умолчанию 5 секунд).
*   Принудительное завершение зависших процессов.

## Лицензия

MIT

