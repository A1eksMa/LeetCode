# execution.py — Функции выполнения кода

**Путь:** `v1.5_PracticeRaptor/core/services/execution.py`

Этот файл содержит **чистые функции** для выполнения и проверки пользовательского кода. Он объединяет логику валидации синтаксиса, извлечения имени функции и запуска тестов, используя интерфейс `ICodeExecutor`.

---

## `validate_code_syntax` — Валидация синтаксиса Python-кода

```python
import ast

from core.domain.result import Ok, Err, Result
from core.domain.errors import ValidationError

def validate_code_syntax(code: str) -> Result[str, ValidationError]:
    """Валидирует синтаксис Python-кода."""
    if not code or not code.strip():
        return Err(ValidationError(
            message="Code cannot be empty",
            field="code",
        ))

    try:
        ast.parse(code)
        return Ok(code)
    except SyntaxError as e:
        return Err(ValidationError(
            message=f"Syntax error at line {e.lineno}: {e.msg}",
            field="code",
        ))
```

Эта функция проверяет, является ли переданная строка допустимым Python-кодом. Она использует встроенный модуль `ast` (Abstract Syntax Tree) для парсинга кода. Если код пуст или содержит синтаксические ошибки, возвращается `Err` с соответствующей `ValidationError`.

**Аналогия:** Это как **грамматический корректор** для кода. Он не проверяет, правильно ли решена задача, но точно скажет, если ты неправильно расставил скобки или забыл двоеточие.

---

## `extract_function_name` — Извлечение имени функции из сигнатуры

```python
import re

def extract_function_name(signature: str) -> str:
    """Извлекает имя функции из сигнатуры."""
    # Пример: "def two_sum(nums: list[int], target: int) -> list[int]:"
    match = re.match(r'def\s+(\w+)\s*\(', signature)
    if match:
        return match.group(1)
    return "solution"
```

Эта функция использует регулярные выражения для извлечения имени функции из её сигнатуры (например, `def two_sum(...)` -> `two_sum`). Если имя не найдено, по умолчанию используется `"solution"`.

**Аналогия:** Это как **поиск имени человека в визитке**. Ты ищешь конкретную структуру (`def Имя(...)`) и извлекаешь имя.

---

## `run_tests` — Запуск кода против тестовых случаев

```python
from core.domain.models import TestCase, ExecutionResult
from core.domain.errors import ExecutionError
from core.ports.executors import ICodeExecutor

def run_tests(
    code: str,
    test_cases: tuple[TestCase, ...],
    function_name: str,
    executor: ICodeExecutor,
    timeout_sec: int = 5,
) -> Result[ExecutionResult, ExecutionError]:
    """Запускает код против тестовых случаев."""
    return executor.execute(
        code=code,
        test_cases=test_cases,
        function_name=function_name,
        timeout_sec=timeout_sec,
    )
```

Эта функция делегирует фактическое выполнение кода интерфейсу `ICodeExecutor`. Она является центральной точкой для запуска любых наборов тестов против пользовательского кода.

**Зависимость:** `ICodeExecutor` — это интерфейс (порт), который выполняет низкоуровневую работу по запуску кода.

---

## `run_examples_only` — Запуск кода только на примерах

```python
from core.domain.models import Problem
from core.domain.enums import Language

def run_examples_only(
    code: str,
    problem: Problem,
    language: Language,
    executor: ICodeExecutor,
) -> Result[ExecutionResult, ExecutionError]:
    """Запускает код только на примерах (быстрая проверка)."""
    lang_spec = problem.get_language_spec(language)
    if not lang_spec:
        return Err(ExecutionError(
            message=f"Language {language.value} not supported for this problem",
            error_type="validation",
        ))

    # Конвертируем примеры в тестовые случаи
    example_tests = tuple(
        TestCase(
            input=ex.input,
            expected=ex.output,
            description=f"Example {i+1}",
        )
        for i, ex in enumerate(problem.examples)
    )

    function_name = extract_function_name(lang_spec.function_signature)

    return run_tests(code, example_tests, function_name, executor)
```

Эта функция предназначена для быстрой проверки кода пользователя только на публичных примерах, предоставленных в описании задачи. Она извлекает спецификацию языка, преобразует примеры задачи в объекты `TestCase` и затем вызывает `run_tests`.

**Аналогия:** Это как **предварительный просмотр результата**. Ты хочешь быстро убедиться, что код вообще работает на самых простых случаях, не дожидаясь полного набора тестов.

---

## `run_full_tests` — Запуск кода на всех тестах

```python
def run_full_tests(
    code: str,
    problem: Problem,
    language: Language,
    executor: ICodeExecutor,
) -> Result[ExecutionResult, ExecutionError]:
    """Запускает код против всех тестовых случаев."""
    lang_spec = problem.get_language_spec(language)
    if not lang_spec:
        return Err(ExecutionError(
            message=f"Language {language.value} not supported for this problem",
            error_type="validation",
        ))

    function_name = extract_function_name(lang_spec.function_signature)

    return run_tests(code, problem.test_cases, function_name, executor)
```

Похожа на `run_examples_only`, но запускает код на *всех* тестовых случаях задачи, включая скрытые. Это используется для окончательной проверки решения.

**Аналогия:** Это как **полноценный экзамен**. Твой код проверяется по всем возможным сценариям, чтобы убедиться в его корректности и надежности.

---

## Взаимодействие с исполнителем кода

```mermaid
graph TD
    A[Пользовательский код] -->|Через ICodeExecutor|
    B[run_examples_only или run_full_tests]
    B -->|Подготовка TestCase, извлечение function_name|
    C(run_tests) -->|Вызов executor.execute|
    D[ICodeExecutor (например, LocalExecutor)]
    D -->|Возвращает ExecutionResult|
    C -->|Возвращает Result|
    B -->|Возвращает Result|
```
