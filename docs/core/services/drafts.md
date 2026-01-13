# drafts.py — Функции управления черновиками

**Путь:** `v1.5_PracticeRaptor/core/services/drafts.py`

Этот файл содержит **чистые функции** для работы с черновиками пользовательского кода. Эти функции реализуют бизнес-логику, связанную с сохранением, получением и удалением черновиков, используя интерфейс `IDraftRepository`.

---

## Ключевой принцип: Чистые функции (Pure Functions)

Все функции в этом файле являются "чистыми":
- Они не изменяют никакого внешнего состояния.
- Они всегда возвращают один и тот же результат для одних и тех же входных данных.
- Они не имеют побочных эффектов (кроме возврата `Result`).

**Аналогия:** Это как **математические формулы**. `f(x) = x + 1` всегда даст `2`, если `x=1`, и не изменит ничего вокруг.

---

## `get_draft` — Получение существующего черновика

```python
from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError
from core.ports.repositories import IDraftRepository

def get_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    draft_repo: IDraftRepository,
) -> Result[Draft, NotFoundError]:
    """Получить существующий черновик."""
    return draft_repo.get(user_id, problem_id, language)
```

Эта функция просто делегирует вызов методу `get` репозитория черновиков. Она служит удобной точкой доступа для бизнес-логики.

**Зависимость:** `IDraftRepository` — это интерфейс (порт), через который функция общается с хранилищем черновиков.

---

## `save_draft` — Сохранение или обновление черновика

```python
from datetime import datetime

# ... импорты ...

def save_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    code: str,
    draft_repo: IDraftRepository,
) -> Result[Draft, StorageError]:
    """Сохранить или обновить черновик."""
    draft = Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )
    return draft_repo.save(draft)
```

Эта функция создает новый объект `Draft` (или обновляет существующий, если репозиторий поддерживает такую логику при `save`). Она автоматически устанавливает `updated_at` на текущее время. Затем она делегирует сохранение репозиторию.

**Аналогия:** Это как **написание письма и отправка его на почту**. Ты создаешь письмо (объект `Draft`), ставишь на нем дату (текущее время), а затем отдаешь его почтовой службе (`draft_repo.save`), которая позаботится о его доставке/хранении.

---

## `delete_draft` — Удаление черновика

```python
def delete_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    draft_repo: IDraftRepository,
) -> Result[None, NotFoundError]:
    """Удалить черновик после успешной отправки решения."""
    return draft_repo.delete(user_id, problem_id, language)
```

Эта функция удаляет черновик, обычно после того, как пользователь успешно отправил решение задачи. Как и `get_draft`, она просто делегирует операцию соответствующему репозиторию.

---

## `get_or_create_code` — Получение кода черновика или шаблона

```python
def get_or_create_code(
    user_id: str,
    problem_id: int,
    language: Language,
    signature: str,
    draft_repo: IDraftRepository,
) -> str:
    """Получить код черновика или вернуть шаблон с сигнатурой."""
    result = get_draft(user_id, problem_id, language, draft_repo)
    match result:
        case Ok(draft):
            return draft.code
        case Err(_):
            # Return template with just the signature
            return f"{signature}\n    pass"
```

Эта функция пытается получить черновик. Если черновик существует (`Ok(draft)`), возвращается его код. Если черновика нет (`Err(_)`), она возвращает базовый шаблон кода, состоящий только из сигнатуры функции задачи и ключевого слова `pass` (для Python). Это обеспечивает, что у пользователя всегда есть отправная точка для решения задачи.

**Аналогия:** Это как **блокнот с начальными заметками**. Если у тебя уже есть незаконченные записи по теме (черновик), ты продолжаешь их. Если нет — даем тебе чистый лист с заголовком (сигнатурой), чтобы ты начал писать.

---

## Взаимодействие с репозиторием черновиков

```mermaid
graph TD
    A[Клиент/Сервис] -->|Вызывает save_draft|
    B(save_draft) -->|Создает Draft|
    C(Draft) -->|Вызывает draft_repo.save|
    D[IDraftRepository (например, JsonDraftRepository)]

    E[Клиент/Сервис] -->|Вызывает get_or_create_code|
    F(get_or_create_code) -->|Вызывает get_draft|
    G(get_draft) -->|Вызывает draft_repo.get|
    H[IDraftRepository (например, JsonDraftRepository)]
    H -->|Возвращает Draft или NotFoundError|
    F -->|Возвращает код черновика или шаблон|
```

