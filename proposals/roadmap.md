# Roadmap: Этапы развития LeetCode Bot

## Этап 1: Прототипирование

### Цель этапа
Проверить концепцию и отладить ядро системы — логику выполнения пользовательского кода и проверки решений. Минимальный работающий продукт без внешних зависимостей.

### Технологический стек
| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.10+ |
| Хранение данных | JSON-файлы |
| Интерфейс | CLI (командная строка) |
| Зависимости | Минимум: только стандартная библиотека Python |

### Основная функциональность
- Загрузка задачи из JSON-файла
- Отображение условия задачи и примеров
- Приём кода решения от пользователя
- Выполнение кода против набора тестов
- Вывод результата: успех / ошибка с описанием

**Что НЕ входит в этап:**
- Telegram-бот
- База данных
- Учёт и статистика пользователей
- Фильтрация задач по темам/сложности
- Подсказки и теория
- Режим быстрой проверки (только полная отправка)

### Архитектура и структура проекта

```
leetcode-prototype/
├── main.py                 # Точка входа, CLI интерфейс
├── task_loader.py          # Загрузка задач из JSON
├── executor.py             # Выполнение пользовательского кода
├── validator.py            # Сравнение результатов с ожидаемыми
├── selector.py             # Выбор задачи из списка
├── tasks/
│   ├── 1_two_sum.json        # Задача 1
│   ├── 2_reverse_string.json # Задача 2
│   └── 3_palindrome.json     # Задача 3
└── README.md
```

### Формат JSON-файла задачи
```json
{
  "id": 1,
  "title": "Two Sum",
  "difficulty": "easy",
  "tags": ["array", "hash-table"],
  "description": "Дан массив целых чисел nums и целое число target. Верните индексы двух чисел, сумма которых равна target.\n\nМожно предположить, что каждый вход имеет ровно одно решение, и вы не можете использовать один и тот же элемент дважды.\n\nВернуть ответ можно в любом порядке.",
  "examples": [
    {
      "input": {"nums": [2, 7, 11, 15], "target": 9},
      "output": [0, 1],
      "explanation": "nums[0] + nums[1] = 2 + 7 = 9, поэтому возвращаем [0, 1]"
    },
    {
      "input": {"nums": [3, 2, 4], "target": 6},
      "output": [1, 2],
      "explanation": "nums[1] + nums[2] = 2 + 4 = 6, поэтому возвращаем [1, 2]"
    },
    {
      "input": {"nums": [3, 3], "target": 6},
      "output": [0, 1],
      "explanation": "nums[0] + nums[1] = 3 + 3 = 6, поэтому возвращаем [0, 1]"
    }
  ],
  "test_cases": [
    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1], "description": "базовый случай из примера"},
    {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2], "description": "ответ не в начале массива"},
    {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1], "description": "одинаковые элементы"},
    {"input": {"nums": [1, 5, 3, 7, 2], "target": 8}, "expected": [1, 2], "description": "несколько элементов"},
    {"input": {"nums": [-1, -2, -3, -4, -5], "target": -8}, "expected": [2, 4], "description": "отрицательные числа"},
    {"input": {"nums": [0, 4, 3, 0], "target": 0}, "expected": [0, 3], "description": "нули в массиве"},
    {"input": {"nums": [1, 2], "target": 3}, "expected": [0, 1], "description": "минимальный массив"}
  ],
  "python3": {
    "function_signature": "def two_sum(nums: list[int], target: int) -> list[int]:",
    "solutions": [
      {
        "name": "Brute Force",
        "complexity": "O(n²)",
        "code": "def two_sum(nums: list[int], target: int) -> list[int]:\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []"
      },
      {
        "name": "Hash Map (один проход)",
        "complexity": "O(n)",
        "code": "def two_sum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []"
      },
      {
        "name": "Hash Map (два прохода)",
        "complexity": "O(n)",
        "code": "def two_sum(nums: list[int], target: int) -> list[int]:\n    num_to_index = {num: i for i, num in enumerate(nums)}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in num_to_index and num_to_index[complement] != i:\n            return [i, num_to_index[complement]]\n    return []"
      }
    ]
  }
}
```

### Применяемые решения
- **Выполнение кода**: `exec()` с ограниченным `globals`/`locals` контекстом
- **Базовая защита**: таймаут через `signal.alarm()` (Unix) или `threading.Timer`
- **Сравнение результатов**: прямое сравнение Python-объектов
- **Вывод ошибок**: перехват исключений с traceback

### Технические требования
| Параметр | Требование |
|----------|------------|
| CPU | 1 vCPU (любой) |
| RAM | 512 MB |
| Disk | 100 MB |
| OS | Любая с Python 3.9+ |
| Сеть | Не требуется |

### Критерии завершения этапа
- [ ] Загрузка задачи из JSON работает корректно
- [ ] Код пользователя выполняется в изолированном контексте
- [ ] Тесты прогоняются последовательно, останавливаются на первой ошибке
- [ ] Корректно обрабатываются: синтаксические ошибки, runtime ошибки, таймауты
- [ ] Результат выводится с понятным описанием

---

## Этап 2: Развитие и масштабирование

### Цель этапа
Превратить прототип в полноценный продукт с пользовательским интерфейсом (Telegram-бот), базой данных и расширенной функциональностью.

### Технологический стек
| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11+ |
| Telegram Bot | aiogram 3.x (асинхронный) |
| База данных | SQLite 3 |
| ORM | SQLAlchemy 2.0 (async) + aiosqlite |
| API | FastAPI (для Code Runner) |
| HTTP Client | httpx (async) |
| Валидация | Pydantic v2 |

### Основная функциональность
- **Telegram-бот** как основной интерфейс
- **Настройки пользователя**: выбор тематики и сложности
- **Фильтрация задач**: по теме, сложности
- **Список задач**: навигация вперед/назад
- **Рандомная задача**: быстрый старт с учётом фильтров
- **Режим решения**:
  - Просмотр условия и примеров
  - Быстрая проверка на примерах (кнопка "Проверить")
  - Полная проверка (кнопка "Отправить")
- **Подсказки**: команда `/help` с теорией
- **Базовая статистика**: какие задачи решены пользователем
- **Хранение решений**: история submissions

### Архитектура и структура проекта

```
leetcode-bot/
├── docker-compose.yml
├── bot/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа бота
│   │   ├── config.py            # Конфигурация
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── start.py         # /start, приветствие
│   │   │   ├── settings.py      # Настройки фильтров
│   │   │   ├── tasks.py         # Список задач, навигация
│   │   │   └── solve.py         # Процесс решения
│   │   ├── keyboards/
│   │   │   ├── inline.py        # Inline-кнопки
│   │   │   └── reply.py         # Reply-клавиатуры
│   │   ├── states/
│   │   │   └── solving.py       # FSM состояния решения
│   │   ├── services/
│   │   │   ├── task_service.py  # Работа с задачами
│   │   │   └── runner_client.py # Клиент к Runner API
│   │   ├── db/
│   │   │   ├── database.py      # Подключение к SQLite
│   │   │   ├── models.py        # SQLAlchemy модели
│   │   │   └── repositories.py  # CRUD операции
│   │   └── utils/
│   └── tests/
├── runner/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py              # FastAPI приложение
│   │   ├── executor.py          # Выполнение кода
│   │   ├── schemas.py           # Pydantic схемы
│   │   └── sandbox.py           # Изоляция (subprocess + limits)
│   └── tests/
├── data/
│   ├── tasks.db                 # SQLite база
│   └── seed/
│       └── tasks.json           # Начальные данные для импорта
└── scripts/
    └── seed_db.py               # Скрипт заполнения БД
```

### Схема базы данных (SQLite)

```sql
-- Темы задач
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

-- Задачи
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    function_signature TEXT NOT NULL,
    examples TEXT NOT NULL,  -- JSON
    hints TEXT,              -- JSON array
    is_active INTEGER DEFAULT 1
);

-- Связь задач и тем
CREATE TABLE task_topics (
    task_id INTEGER REFERENCES tasks(id),
    topic_id INTEGER REFERENCES topics(id),
    PRIMARY KEY (task_id, topic_id)
);

-- Тест-кейсы
CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER REFERENCES tasks(id),
    input TEXT NOT NULL,      -- JSON
    expected TEXT NOT NULL,   -- JSON
    is_example INTEGER DEFAULT 0,
    description TEXT
);

-- Пользователи
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    settings TEXT DEFAULT '{}',  -- JSON
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Решения
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    task_id INTEGER REFERENCES tasks(id),
    code TEXT NOT NULL,
    status TEXT NOT NULL,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Применяемые решения
- **Асинхронность**: aiogram 3.x + aiosqlite для неблокирующей работы
- **FSM**: Finite State Machine для управления состоянием диалога (выбор фильтров → список → решение)
- **Code Runner**: отдельный FastAPI сервис, изоляция через subprocess с ресурсными лимитами
- **Контейнеризация**: Docker Compose для локальной разработки
- **Миграции**: Alembic для управления схемой БД

### Технические требования
| Параметр | Требование |
|----------|------------|
| CPU | 2 vCPU |
| RAM | 2 GB |
| Disk | 20 GB SSD |
| OS | Ubuntu 22.04 / Debian 12 |
| Docker | 24+ |
| Сеть | Доступ к Telegram API |

### Критерии завершения этапа
- [ ] Telegram-бот отвечает на команды и ведёт диалог
- [ ] Работает фильтрация и навигация по задачам
- [ ] Пользователь может решать задачи через бота
- [ ] Решения сохраняются в SQLite
- [ ] Базовая статистика пользователя доступна
- [ ] Проект запускается через `docker-compose up`

---

## Этап 3: Техническая зрелость

### Цель этапа
Подготовить систему к production-нагрузкам: надёжность, масштабируемость, безопасность, мониторинг. Полная реализация функциональных требований.

### Технологический стек
| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11+ |
| Telegram Bot | aiogram 3.x |
| API Gateway | FastAPI |
| База данных | PostgreSQL 15+ (отдельный сервер) |
| Кэш/Очереди | Redis 7+ |
| ORM | SQLAlchemy 2.0 + asyncpg |
| Task Queue | arq / Celery |
| Контейнеризация | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Reverse Proxy | Nginx |
| Мониторинг | Prometheus + Grafana |
| Логирование | Структурированные логи (JSON), Loki (опционально) |

### Основная функциональность
Всё из этапа 2, плюс:

- **Регистрация и авторизация** пользователей
- **Расширенная статистика**: решённые задачи, процент успеха, время, прогресс
- **Фильтр "только нерешённые"** для зарегистрированных
- **Просмотр решений** других пользователей
- **Добавление тест-кейсов** пользователями
- **Поддержка нескольких языков** программирования (Go, Java, etc.)
- **Rate limiting** и защита от злоупотреблений
- **Webhooks** вместо polling для бота
- **Health checks** и graceful shutdown
- **Автоматический деплой** при пуше в main

### Архитектура и структура проекта

```
                    ┌─────────────────────────────────────────┐
                    │              Load Balancer              │
                    │                (Nginx)                  │
                    └──────────────────┬──────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
    ┌───────────────┐         ┌───────────────┐          ┌───────────────┐
    │  Bot Service  │         │  Bot Service  │          │  API Gateway  │
    │   (webhook)   │         │   (webhook)   │          │   (FastAPI)   │
    └───────┬───────┘         └───────┬───────┘          └───────┬───────┘
            │                         │                          │
            └─────────────────────────┼──────────────────────────┘
                                      │
                                      ▼
                             ┌───────────────┐
                             │     Redis     │
                             │ (cache/queue) │
                             └───────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │ Runner Worker│ │ Runner Worker│ │ Runner Worker│
           │   (Python)   │ │    (Go)      │ │   (Java)     │
           └──────────────┘ └──────────────┘ └──────────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                                     ▼
                            ┌───────────────┐
                            │  PostgreSQL   │
                            │   (Primary)   │
                            └───────────────┘
```

```
leetcode-bot/
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx/
│   └── nginx.conf
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── bot/
│   ├── Dockerfile
│   └── src/
│       ├── main.py
│       ├── config.py
│       ├── handlers/
│       ├── keyboards/
│       ├── states/
│       ├── services/
│       ├── middlewares/
│       │   ├── auth.py
│       │   ├── rate_limit.py
│       │   └── logging.py
│       └── db/
├── api/
│   ├── Dockerfile
│   └── src/
│       ├── main.py
│       ├── routers/
│       │   ├── tasks.py
│       │   ├── submissions.py
│       │   ├── users.py
│       │   └── solutions.py
│       ├── services/
│       ├── schemas/
│       └── db/
│           ├── database.py
│           ├── models.py
│           └── migrations/
├── runner/
│   ├── Dockerfile
│   ├── Dockerfile.python
│   ├── Dockerfile.go
│   ├── Dockerfile.java
│   └── src/
│       ├── worker.py
│       ├── executors/
│       │   ├── base.py
│       │   ├── python_executor.py
│       │   ├── go_executor.py
│       │   └── java_executor.py
│       └── sandbox/
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       └── dashboards/
└── scripts/
    ├── deploy.sh
    └── backup.sh
```

### Применяемые решения
- **Горизонтальное масштабирование**: несколько инстансов бота за Nginx
- **Webhook mode**: вместо polling для снижения нагрузки
- **Очередь задач**: Redis + arq для асинхронного выполнения кода
- **Docker sandbox**: изолированные контейнеры для каждого языка
- **CI/CD**: автотесты → сборка образов → деплой через SSH
- **Мониторинг**: Prometheus метрики, Grafana дашборды
- **Graceful shutdown**: корректное завершение при деплое

### Безопасность
- **Code sandbox**: Docker с ограничениями (CPU, RAM, время, сеть отключена)
- **Rate limiting**: per-user лимиты на submissions
- **Secrets**: все ключи в переменных окружения / Docker secrets
- **HTTPS**: SSL termination на Nginx
- **Валидация**: Pydantic на всех входных данных

### Технические требования

**Application Server:**
| Параметр | Минимум | Рекомендуется |
|----------|---------|---------------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Disk | 40 GB SSD | 80 GB SSD |

**Database Server:**
| Параметр | Минимум | Рекомендуется |
|----------|---------|---------------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Disk | 50 GB SSD | 100 GB SSD |

**Общие требования:**
- OS: Ubuntu 22.04 LTS / Debian 12
- Docker 24+
- PostgreSQL 15+
- Redis 7+
- Сеть: 100 Mbps+, статический IP

### Критерии завершения этапа
- [ ] PostgreSQL на отдельном сервере, миграции работают
- [ ] Redis для кэширования и очереди задач
- [ ] CI/CD пайплайн: push → тесты → деплой
- [ ] Мониторинг и алерты настроены
- [ ] Поддержка минимум 2 языков программирования
- [ ] Rate limiting и защита от злоупотреблений
- [ ] Документация API (OpenAPI/Swagger)
- [ ] Uptime 99%+ при нормальной нагрузке

---

## Сводная таблица этапов

| Характеристика | Этап 1 | Этап 2 | Этап 3 |
|----------------|--------|--------|--------|
| **Интерфейс** | CLI | Telegram Bot | Telegram Bot |
| **База данных** | JSON-файлы | SQLite | PostgreSQL |
| **Кэш** | — | — | Redis |
| **Контейнеры** | — | Docker Compose | Docker + CI/CD |
| **Языки задач** | Python | Python | Python, Go, Java |
| **Пользователи** | — | Базовый учёт | Полная статистика |
| **Фильтрация** | — | Да | Да + "нерешённые" |
| **Масштабирование** | — | Вертикальное | Горизонтальное |
| **Сервер** | Любой ПК | 2 vCPU / 2 GB | 4+ vCPU / 8+ GB |
