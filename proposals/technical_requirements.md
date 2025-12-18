# Технические требования к LeetCode Telegram Bot

## 1. Архитектура системы

### 1.1. Общая архитектура
Система построена на микросервисной архитектуре и состоит из следующих компонентов:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Telegram      │     │   Bot Service   │     │   PostgreSQL    │
│   Users         │◄───►│   (aiogram)     │◄───►│   Database      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   API Gateway   │
                        │   (FastAPI)     │
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │  Python   │ │   Go      │ │   Java    │
            │  Runner   │ │  Runner   │ │  Runner   │
            │  (MVP)    │ │ (future)  │ │ (future)  │
            └───────────┘ └───────────┘ └───────────┘
```

### 1.2. Компоненты системы

| Компонент | Назначение | Технология |
|-----------|------------|------------|
| Bot Service | Telegram-интерфейс, обработка команд | Python 3.11+, aiogram 3.x |
| API Gateway | Маршрутизация запросов, аутентификация | Python 3.11+, FastAPI |
| Code Runner API | Выполнение пользовательского кода | FastAPI + Docker sandbox |
| Database | Хранение задач, пользователей, решений | PostgreSQL 15+ |
| Cache | Кэширование сессий и частых запросов | Redis |
| Message Queue | Очередь задач на выполнение кода | Redis / RabbitMQ |

## 2. Технологический стек

### 2.1. Backend
- **Язык**: Python 3.11+
- **Telegram Bot Framework**: aiogram 3.x (асинхронный)
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async) + Alembic (миграции)
- **Валидация данных**: Pydantic v2
- **HTTP Client**: httpx (async)

### 2.2. База данных и кэширование
- **Основная БД**: PostgreSQL 15+
- **Кэш/Сессии**: Redis 7+
- **Очередь задач**: Redis (через arq или Celery с Redis backend)

### 2.3. Инфраструктура
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx (опционально, для production)
- **Мониторинг**: Prometheus + Grafana (опционально)

## 3. Структура проекта

```
leetcode-bot/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       ├── ci.yml              # Линтинг, тесты
│       └── deploy.yml          # Автодеплой
├── bot/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py             # Точка входа
│   │   ├── config.py           # Конфигурация
│   │   ├── handlers/           # Обработчики команд
│   │   │   ├── __init__.py
│   │   │   ├── start.py
│   │   │   ├── tasks.py
│   │   │   ├── solutions.py
│   │   │   └── settings.py
│   │   ├── keyboards/          # Inline и reply клавиатуры
│   │   ├── states/             # FSM состояния
│   │   ├── middlewares/        # Middleware (логирование, авторизация)
│   │   ├── services/           # Бизнес-логика, API клиенты
│   │   └── utils/
│   └── tests/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py        # CRUD задач
│   │   │   ├── submissions.py  # Отправка решений
│   │   │   └── users.py        # Пользователи
│   │   ├── models/             # SQLAlchemy модели
│   │   ├── schemas/            # Pydantic схемы
│   │   ├── services/
│   │   └── db/
│   │       ├── database.py
│   │       └── migrations/
│   └── tests/
├── runner/
│   ├── Dockerfile
│   ├── Dockerfile.sandbox      # Изолированный образ для выполнения кода
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── executor.py         # Логика выполнения кода
│   │   └── sandbox.py          # Управление sandbox-контейнерами
│   └── tests/
└── shared/
    └── schemas/                # Общие Pydantic схемы
```

## 4. Схема базы данных

### 4.1. Основные таблицы

```sql
-- Пользователи
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'
);

-- Темы задач
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL
);

-- Задачи
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    function_signature TEXT NOT NULL,
    examples JSONB NOT NULL,
    hints TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Связь задач и тем (M2M)
CREATE TABLE task_topics (
    task_id INT REFERENCES tasks(id) ON DELETE CASCADE,
    topic_id INT REFERENCES topics(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, topic_id)
);

-- Тест-кейсы
CREATE TABLE test_cases (
    id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks(id) ON DELETE CASCADE,
    input JSONB NOT NULL,
    expected_output JSONB NOT NULL,
    is_example BOOLEAN DEFAULT FALSE,  -- Показывается в условии
    description TEXT,
    order_index INT DEFAULT 0
);

-- Решения пользователей
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    task_id INT REFERENCES tasks(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    language VARCHAR(20) NOT NULL DEFAULT 'python',
    status VARCHAR(20) NOT NULL,  -- pending, running, accepted, wrong_answer, error, timeout
    execution_time_ms INT,
    memory_used_kb INT,
    error_message TEXT,
    failed_test_id INT REFERENCES test_cases(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_submissions_user_task ON submissions(user_id, task_id);
CREATE INDEX idx_tasks_difficulty ON tasks(difficulty);
CREATE INDEX idx_test_cases_task ON test_cases(task_id);
```

### 4.2. Настройки пользователя (JSONB)
```json
{
  "preferred_language": "python",
  "difficulty_filter": ["easy", "medium"],
  "topic_filter": [1, 3, 5],
  "notifications_enabled": true
}
```

## 5. API Specification

### 5.1. API Gateway Endpoints

#### Задачи
```
GET    /api/v1/tasks                    # Список задач с фильтрацией
GET    /api/v1/tasks/{task_id}          # Детали задачи
GET    /api/v1/tasks/random             # Случайная задача по фильтрам
GET    /api/v1/tasks/{task_id}/hints    # Подсказки к задаче
GET    /api/v1/tasks/{task_id}/solutions # Решения других пользователей
```

#### Решения
```
POST   /api/v1/submissions              # Отправить решение
GET    /api/v1/submissions/{id}         # Статус решения
POST   /api/v1/submissions/check        # Быстрая проверка на примерах
```

#### Пользователи
```
POST   /api/v1/users                    # Регистрация/обновление пользователя
GET    /api/v1/users/{telegram_id}      # Данные пользователя
GET    /api/v1/users/{telegram_id}/stats # Статистика пользователя
PATCH  /api/v1/users/{telegram_id}/settings # Обновить настройки
```

#### Справочники
```
GET    /api/v1/topics                   # Список тем
GET    /api/v1/languages                # Поддерживаемые языки
```

### 5.2. Пример запроса/ответа

**POST /api/v1/submissions**
```json
// Request
{
  "task_id": 42,
  "user_telegram_id": 123456789,
  "code": "def two_sum(nums, target):\n    ...",
  "language": "python",
  "mode": "submit"  // "check" для быстрой проверки
}

// Response
{
  "submission_id": "abc123",
  "status": "pending"
}
```

**GET /api/v1/submissions/{id}** (после выполнения)
```json
{
  "submission_id": "abc123",
  "status": "accepted",
  "execution_time_ms": 45,
  "memory_used_kb": 14200,
  "tests_passed": 15,
  "tests_total": 15
}
```

## 6. Code Runner (Sandbox)

### 6.1. Требования безопасности
- Выполнение кода в изолированном Docker-контейнере
- Ограничение ресурсов:
  - CPU: 1 core
  - Memory: 256 MB
  - Timeout: 10 секунд
  - Disk: 10 MB (только /tmp)
  - Network: отключена
- Запуск от непривилегированного пользователя
- Read-only filesystem (кроме /tmp)
- Seccomp profile для ограничения syscalls

### 6.2. Процесс выполнения
1. Получение задачи из очереди
2. Создание временного контейнера с кодом пользователя
3. Последовательный запуск тест-кейсов
4. Сбор метрик (время, память)
5. Остановка при первой ошибке
6. Возврат результата через callback/webhook

### 6.3. Dockerfile.sandbox (Python)
```dockerfile
FROM python:3.11-slim

RUN useradd -m -s /bin/bash runner && \
    mkdir /app && chown runner:runner /app

USER runner
WORKDIR /app

# Минимальный набор библиотек для алгоритмических задач
COPY requirements.sandbox.txt .
RUN pip install --user --no-cache-dir -r requirements.sandbox.txt

COPY --chown=runner:runner runner.py .

CMD ["python", "runner.py"]
```

## 7. CI/CD Pipeline

### 7.1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/leetcode-bot
            git pull origin main
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
            docker system prune -f
```

### 7.2. Этапы пайплайна
1. **Lint** — ruff, mypy
2. **Test** — pytest с coverage
3. **Build** — сборка Docker образов
4. **Push** — загрузка в Container Registry (DockerHub / GitHub CR)
5. **Deploy** — обновление на production сервере

## 8. Docker Compose

### 8.1. Development (docker-compose.yml)
```yaml
version: '3.8'

services:
  bot:
    build: ./bot
    env_file: .env
    depends_on:
      - api
      - redis
    restart: unless-stopped

  api:
    build: ./api
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - redis
    restart: unless-stopped

  runner:
    build: ./runner
    env_file: .env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: leetcode
      POSTGRES_USER: leetcode
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## 9. Конфигурация

### 9.1. Переменные окружения (.env.example)
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=leetcode
DB_USER=leetcode
DB_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis:6379/0

# API
API_URL=http://api:8000
API_SECRET_KEY=your_secret_key

# Runner
RUNNER_TIMEOUT_SEC=10
RUNNER_MEMORY_LIMIT_MB=256
RUNNER_CPU_LIMIT=1

# Environment
ENV=development  # development | production
LOG_LEVEL=INFO
```

## 10. Требования к серверу (Production)

### 10.1. Минимальные требования
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Disk**: 40 GB SSD
- **OS**: Ubuntu 22.04 LTS / Debian 12

### 10.2. Рекомендуемые требования
- **CPU**: 4 vCPU
- **RAM**: 8 GB
- **Disk**: 80 GB SSD
- **Network**: 100 Mbps

### 10.3. Требуемое ПО
- Docker 24+
- Docker Compose v2
- Git

## 11. Масштабирование (Future)

### 11.1. Горизонтальное масштабирование
- Несколько инстансов Bot Service за load balancer
- Несколько Runner workers для параллельного выполнения кода
- Read replicas для PostgreSQL

### 11.2. Добавление новых языков
Для каждого нового языка программирования:
1. Создать Dockerfile.sandbox.{lang}
2. Реализовать runner адаптер
3. Добавить language в конфигурацию
4. Обновить схему БД (function_signature для языка)

## 12. Метрики и мониторинг

### 12.1. Ключевые метрики
- Количество активных пользователей (DAU/MAU)
- Количество submissions в минуту
- Среднее время выполнения кода
- Процент успешных решений
- Latency API endpoints
- Ошибки и exceptions

### 12.2. Health checks
```
GET /health         # API health
GET /health/db      # Database connectivity
GET /health/redis   # Redis connectivity
```

## 13. Безопасность

### 13.1. Защита API
- Rate limiting (per user, per IP)
- Валидация всех входных данных через Pydantic
- CORS политика
- Секреты в переменных окружения (никогда в коде)

### 13.2. Защита Code Runner
- Полная изоляция в Docker
- Ограничение ресурсов (CPU, RAM, время)
- Отключение сети в sandbox
- Whitelist разрешённых модулей Python

### 13.3. Данные пользователей
- Минимальный сбор данных (только telegram_id, username)
- Хэширование чувствительных данных (если появятся)
- Регулярное резервное копирование БД
