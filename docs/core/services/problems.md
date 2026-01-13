# problems.py — Функции управления задачами

**Путь:** `v1.5_PracticeRaptor/core/services/problems.py`

Этот файл содержит **чистые функции** для работы с задачами (проблемами). Эти функции реализуют бизнес-логику для получения, фильтрации и выбора случайных задач, используя интерфейс `IProblemRepository`.

---

## `get_problem` — Получение задачи по ID

```python
from core.domain.models import Problem
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError
from core.ports.repositories import IProblemRepository

def get_problem(
    problem_id: int,
    repo: IProblemRepository,
) -> Result[Problem, NotFoundError]:
    """Получить задачу по ID."""
    return repo.get_by_id(problem_id)
```

Эта функция служит прямой оберткой для метода `get_by_id` репозитория задач. Она обеспечивает простой способ получения конкретной задачи по её уникальному идентификатору.

**Зависимость:** `IProblemRepository` — это интерфейс (порт) для взаимодействия с хранилищем задач.

---

## `get_all_problems` — Получение всех задач

```python
def get_all_problems(repo: IProblemRepository) -> tuple[Problem, ...]:
    """Получить все задачи, отсортированные по ID."""
    return repo.get_all()
```

Возвращает все доступные задачи. Предполагается, что репозиторий возвращает их в отсортированном порядке (например, по ID).

**Аналогия:** Это как **просмотр всего списка доступных курсов** на образовательной платформе.

---

## `filter_problems` — Фильтрация задач по критериям

```python
from core.domain.enums import Difficulty, Language

def filter_problems(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    tags: tuple[str, ...] | None = None,
    language: Language | None = None,
) -> tuple[Problem, ...]:
    """Фильтровать задачи по критериям."""
    return repo.filter(difficulty=difficulty, tags=tags, language=language)
```

Эта функция позволяет находить задачи, соответствующие определенным критериям, таким как сложность, теги или поддерживаемый язык. Она также делегирует логику фильтрации репозиторию.

**Аналогия:** Это как **использование фильтров поиска** на сайте: "показать только легкие задачи по массивам для Python".

---

## `get_random_problem` — Получение случайной задачи

```python
import random

def get_random_problem(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    tags: tuple[str, ...] | None = None,
    language: Language | None = None,
    exclude_ids: tuple[int, ...] = (),
) -> Result[Problem, NotFoundError]:
    """Получить случайную задачу, соответствующую критериям."""
    problems = filter_problems(repo, difficulty, tags, language)
    available = tuple(p for p in problems if p.id not in exclude_ids)

    if not available:
        return Err(NotFoundError(
            entity="Problem",
            id="random",
        ))

    return Ok(random.choice(available))
```

Функция сначала фильтрует все задачи по заданным критериям, затем исключает задачи с указанными ID (чтобы не выдавать уже решенные или текущие задачи) и выбирает случайную из оставшихся. Если подходящих задач нет, возвращает `NotFoundError`.

**Аналогия:** Это как **рулетка с задачами**, но с возможностью сказать: "только легкие задачи, не те, что я уже решал".

---

## `get_problem_display_text` — Получение текста задачи для отображения

```python
def get_problem_display_text(
    problem: Problem,
    locale: str = "en",
) -> dict[str, str]:
    """Получить текст задачи для отображения."""
    return {
        "title": problem.title.get(locale),
        "description": problem.description.get(locale),
        "difficulty": problem.difficulty.value,
        "tags": ", ".join(problem.tags),
    }
```

Форматирует информацию о задаче в удобный для отображения вид, с учетом локали для заголовка и описания. Возвращает словарь с ключевыми текстовыми полями.

**Аналогия:** Это как **создание карточки товара** для онлайн-магазина, где ты собираешь всю нужную информацию о товаре (задаче) и представляешь её в красивом виде.

---

## `format_examples` — Форматирование примеров для отображения

```python
def format_examples(
    problem: Problem,
    locale: str = "en",
) -> list[dict]:
    """Форматировать примеры для отображения."""
    result = []
    for i, example in enumerate(problem.examples, 1):
        item = {
            "number": i,
            "input": example.input,
            "output": example.output,
        }
        if example.explanation:
            item["explanation"] = example.explanation.get(locale)
        result.append(item)
    return result
```

Берет примеры задачи и форматирует их в список словарей, каждый из которых включает номер примера, входные и выходные данные, а также, при наличии, локализованное объяснение.

**Аналогия:** Это как **подготовка слайдов презентации** с примерами. Каждый слайд (элемент списка) показывает вход, ожидаемый результат и пояснение.

---

## Взаимодействие с репозиторием задач

```mermaid
graph TD
    A[Клиент/Сервис] -->|Вызывает get_random_problem|
    B(get_random_problem) -->|Вызывает filter_problems|
    C(filter_problems) -->|Вызывает repo.filter|
    D[IProblemRepository (например, JsonProblemRepository)]
    D -->|Возвращает список Problem|
    C -->|Возвращает отфильтрованный список|
    B -->|Выбирает случайную Problem, исключая exclude_ids|
    B -->|Возвращает Result[Problem, NotFoundError]|
```
