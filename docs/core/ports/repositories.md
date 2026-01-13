# repositories.py — Интерфейсы хранилищ данных (Порты)

**Путь:** `v1.5_PracticeRaptor/core/ports/repositories.py`

Этот файл определяет **как система сохраняет и извлекает данные**. Он содержит интерфейсы (контракты) для работы с различными сущностями домена (задачи, пользователи, черновики и т.д.), абстрагируясь от конкретных технологий хранения (например, база данных, файловая система, удаленный API).

---

## Общие принципы

Все интерфейсы хранилищ наследуются от `Protocol`, что позволяет любому классу, реализующему описанные методы, считаться соответствующим этому протоколу.

Возвращаемый тип `Result` (из `core.domain.result`) используется для обработки как успешных операций, так и возможных ошибок (`NotFoundError`, `StorageError`).

---

## `IProblemRepository` — Интерфейс хранилища задач

```python
from typing import Protocol
from core.domain.models import Problem
from core.domain.enums import Difficulty, Language
from core.domain.result import Result
from core.domain.errors import NotFoundError


class IProblemRepository(Protocol):
    """Интерфейс для хранения задач."""

    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
        """Получить задачу по ID."""
        ...

    def get_all(self) -> tuple[Problem, ...]:
        """Получить все задачи."""
        ...

    def filter(
        self,
        difficulty: Difficulty | None = None,
        tags: tuple[str, ...] | None = None,
        language: Language | None = None,
    ) -> tuple[Problem, ...]:
        """Фильтровать задачи по критериям."""
        ...

    def count(self) -> int:
        """Получить общее количество задач."""
        ...
```

**Аналогия:** Это как **каталог книг в библиотеке**. Ты можешь найти книгу по номеру (`get_by_id`), посмотреть все книги (`get_all`), найти книги по жанру или автору (`filter`), или узнать, сколько всего книг (`count`).

---

## `IUserRepository` — Интерфейс хранилища пользователей

```python
class IUserRepository(Protocol):
    """Интерфейс для хранения пользователей."""

    def get_by_id(self, user_id: str) -> Result[User, NotFoundError]:
        """Получить пользователя по ID."""
        ...

    def save(self, user: User) -> Result[User, StorageError]:
        """Сохранить пользователя (создать или обновить)."""
        ...

    def delete(self, user_id: str) -> Result[None, NotFoundError]:
        """Удалить пользователя."""
        ...
```

**Аналогия:** Это как **база данных клиентов**. Ты можешь найти клиента по ID, добавить нового или обновить существующего, или удалить запись.

---

## `IDraftRepository` — Интерфейс хранилища черновиков

```python
class IDraftRepository(Protocol):
    """Интерфейс для хранения черновиков."""

    def get(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[Draft, NotFoundError]:
        """Получить черновик для комбинации user/problem/language."""
        ...

    def save(self, draft: Draft) -> Result[Draft, StorageError]:
        """Сохранить черновик (перезаписывает существующий)."""
        ...

    def delete(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[None, NotFoundError]:
        """Удалить черновик."""
        ...

    def get_all_for_user(self, user_id: str) -> tuple[Draft, ...]:
        """Получить все черновики для пользователя."""
        ...
```

**Аналогия:** Это как **папка "Черновики" в твоей электронной почте**. Ты можешь найти конкретный черновик (по пользователю, задаче, языку), сохранить его, удалить, или просмотреть все свои черновики.

---

## `ISubmissionRepository` — Интерфейс хранилища решений

```python
class ISubmissionRepository(Protocol):
    """Интерфейс для хранения решений."""

    def get_by_id(self, submission_id: str) -> Result[Submission, NotFoundError]:
        """Получить решение по ID."""
        ...

    def save(self, submission: Submission) -> Result[Submission, StorageError]:
        """Сохранить новое решение."""
        ...

    def get_for_problem(
        self,
        user_id: str,
        problem_id: int,
    ) -> tuple[Submission, ...]:
        """Получить все решения для user/problem."""
        ...

    def get_for_user(self, user_id: str) -> tuple[Submission, ...]:
        """Получить все решения для пользователя."""
        ...
```

**Аналогия:** Это как **архив сданных работ студента**. Ты можешь найти конкретную работу по её номеру, сохранить новую работу, или просмотреть все работы по конкретной задаче или все работы конкретного студента.

---

## `IProgressRepository` — Интерфейс хранилища прогресса

```python
class IProgressRepository(Protocol):
    """Интерфейс для хранения прогресса."""

    def get(
        self,
        user_id: str,
        problem_id: int,
    ) -> Result[Progress, NotFoundError]:
        """Получить прогресс для user/problem."""
        ...

    def save(self, progress: Progress) -> Result[Progress, StorageError]:
        """Сохранить прогресс."""
        ...

    def get_all_for_user(self, user_id: str) -> tuple[Progress, ...]:
        """Получить все записи прогресса для пользователя."""
        ...

    def get_solved_count(self, user_id: str) -> int:
        """Получить количество решенных задач для пользователя."""
        ...

    def get_solved_by_difficulty(
        self,
        user_id: str,
    ) -> dict[Difficulty, int]:
        """Получить количество решенных задач, сгруппированных по сложности."""
        ...
```

**Аналогия:** Это как **табель успеваемости ученика**. Ты можешь посмотреть прогресс по конкретной задаче, сохранить обновленный прогресс, посмотреть весь прогресс, узнать, сколько задач решено, и даже разбить решенные задачи по сложности.
