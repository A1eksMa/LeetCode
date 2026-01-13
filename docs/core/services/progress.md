# progress.py — Функции управления прогрессом пользователя

**Путь:** `v1.5_PracticeRaptor/core/services/progress.py`

Этот файл содержит **чистые функции** для отслеживания и управления прогрессом пользователя по задачам. Эти функции инкапсулируют бизнес-логику для получения, обновления и расчета статистики прогресса, используя интерфейс `IProgressRepository`.

---

## `get_user_progress` — Получение прогресса пользователя

```python
from core.domain.models import Progress
from core.domain.enums import ProgressStatus
from core.domain.result import Ok, Err
from core.ports.repositories import IProgressRepository

def get_user_progress(
    user_id: str,
    problem_id: int,
    progress_repo: IProgressRepository,
) -> Progress:
    """Получить прогресс пользователя по задаче, создавая начальный, если не существует."""
    result = progress_repo.get(user_id, problem_id)
    match result:
        case Ok(progress):
            return progress
        case Err(_):
            return Progress(
                user_id=user_id,
                problem_id=problem_id,
                status=ProgressStatus.NOT_STARTED,
                attempts=0,
                solved_languages=(),
            )
```

Эта функция пытается получить существующий прогресс пользователя по конкретной задаче. Если прогресс не найден (т.е., пользователь еще не взаимодействовал с этой задачей), она создает и возвращает новый объект `Progress` со статусом `NOT_STARTED`. Это гарантирует, что у каждой задачи всегда будет начальный прогресс для каждого пользователя.

**Аналогия:** Это как **открытие новой страницы в журнале успеваемости** для нового предмета. Если записи уже есть, ты их читаешь; если нет, создаешь пустую страницу, чтобы начать записывать прогресс.

---

## `update_progress_on_attempt` — Обновление прогресса после попытки

```python
from datetime import datetime
from core.domain.enums import Language

def update_progress_on_attempt(
    progress: Progress,
    solved: bool,
    language: Language,
) -> Progress:
    """Создает обновленный прогресс после попытки (неизменяемый)."""
    new_attempts = progress.attempts + 1

    if solved:
        new_languages = progress.solved_languages
        if language not in new_languages:
            new_languages = (*new_languages, language)

        return Progress(
            user_id=progress.user_id,
            problem_id=progress.problem_id,
            status=ProgressStatus.SOLVED,
            attempts=new_attempts,
            solved_languages=new_languages,
            first_solved_at=progress.first_solved_at or datetime.now(),
        )
    else:
        new_status = (
            ProgressStatus.SOLVED
            if progress.status == ProgressStatus.SOLVED
            else ProgressStatus.IN_PROGRESS
        )
        return Progress(
            user_id=progress.user_id,
            problem_id=progress.problem_id,
            status=new_status,
            attempts=new_attempts,
            solved_languages=progress.solved_languages,
            first_solved_at=progress.first_solved_at,
        )
```

Эта функция принимает текущий объект `Progress` и информацию о новой попытке (была ли она успешной и на каком языке) и возвращает *новый* объект `Progress` с обновленными данными. Оригинальный объект `progress` остается неизменным (`frozen=True`).

- Если задача решена (`solved=True`): статус становится `SOLVED`, язык добавляется в `solved_languages` (если его там еще нет), `first_solved_at` устанавливается (если еще не было).
- Если задача не решена: статус становится `IN_PROGRESS` (если раньше не был `SOLVED`), количество попыток увеличивается.

**Аналогия:** Это как **обновление записи в журнале успеваемости**. Ты не исправляешь старую запись, а создаешь новую, которая отражает последнее состояние, например: "Попытка №5: не решено", или "Попытка №6: решено на Python".

---

## `calculate_user_stats` — Расчет общей статистики пользователя

```python
def calculate_user_stats(
    user_id: str,
    progress_repo: IProgressRepository,
) -> dict:
    """Рассчитать общую статистику пользователя."""
    all_progress = progress_repo.get_all_for_user(user_id)

    solved = [p for p in all_progress if p.status == ProgressStatus.SOLVED]
    in_progress = [p for p in all_progress if p.status == ProgressStatus.IN_PROGRESS]

    return {
        "total_solved": len(solved),
        "in_progress": len(in_progress),
        "total_attempts": sum(p.attempts for p in all_progress),
    }
```

Эта функция собирает все записи прогресса для пользователя и рассчитывает агрегированную статистику: общее количество решенных задач, количество задач в процессе и общее количество попыток.

**Аналогия:** Это как **подсчет итоговых оценок** в конце семестра: сколько предметов сдано, сколько еще в работе, сколько раз пересдавал.

---

## `calculate_stats_by_difficulty` — Расчет статистики по сложности

```python
from core.domain.enums import Difficulty

def calculate_stats_by_difficulty(
    user_id: str,
    progress_repo: IProgressRepository,
    problem_difficulties: dict[int, Difficulty],
) -> dict[Difficulty, dict]:
    """Рассчитать статистику, сгруппированную по сложности."""
    all_progress = progress_repo.get_all_for_user(user_id)

    stats: dict[Difficulty, dict] = {d: {"solved": 0, "total": 0} for d in Difficulty}

    for progress in all_progress:
        difficulty = problem_difficulties.get(progress.problem_id)
        if difficulty:
            stats[difficulty]["total"] += 1
            if progress.status == ProgressStatus.SOLVED:
                stats[difficulty]["solved"] += 1

    return stats
```

Эта функция детализирует статистику, группируя её по сложности задач. Для каждой категории сложности (например, `EASY`, `MEDIUM`, `HARD`) она подсчитывает общее количество задач и количество решенных задач. Требует маппинг `problem_id` к `Difficulty`.

**Аналогия:** Это как **анализ успеваемости по типам заданий**: сколько легких задач решено, сколько сложных, и сколько всего было в каждой категории.

---

## Взаимодействие с репозиторием прогресса

```mermaid
graph TD
    A[Клиент/Сервис] -->|Вызывает get_user_progress|
    B(get_user_progress) -->|Вызывает progress_repo.get|
    C[IProgressRepository]
    C -->|Возвращает Progress или NotFoundError|
    B -->|Возвращает Progress (существующий или новый)|

    D[Текущий Progress] -->|Вызывает update_progress_on_attempt|
    E(update_progress_on_attempt) -->|Создает НОВЫЙ Progress|
    E -->|Возвращает обновленный Progress|

    F[Клиент/Сервис] -->|Вызывает calculate_user_stats или calculate_stats_by_difficulty|
    G(calculate_stats_by_difficulty) -->|Вызывает progress_repo.get_all_for_user|
    H[IProgressRepository] -->|Возвращает все Progress для пользователя|
    G -->|Обрабатывает и возвращает статистику|
```
