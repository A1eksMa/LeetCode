# Step 6: Core Services — Report

## Summary

| Metric | Value |
|--------|-------|
| Status | Completed |
| Tests | 238 passed (69 new for services) |
| Coverage | ~90% |
| Duration | ~15 min |

## Implemented

### Problems Service (`core/services/problems.py`)

Pure functions for problem operations:

- `get_problem(problem_id, repo)` — get problem by ID
- `get_all_problems(repo)` — get all problems
- `filter_problems(repo, difficulty, tags, language)` — filter by criteria
- `get_random_problem(repo, ...)` — get random problem with exclusions
- `get_problem_display_text(problem, locale)` — get localized display text
- `format_examples(problem, locale)` — format examples for display

### Execution Service (`core/services/execution.py`)

Pure functions for code execution:

- `validate_code_syntax(code)` — AST-based syntax validation
- `extract_function_name(signature)` — extract function name from signature
- `run_tests(code, test_cases, function_name, executor, timeout)` — run tests
- `run_examples_only(code, problem, language, executor)` — run example tests only
- `run_full_tests(code, problem, language, executor)` — run all test cases

### Progress Service (`core/services/progress.py`)

Pure functions for progress tracking:

- `get_user_progress(user_id, problem_id, repo)` — get or create initial progress
- `update_progress_on_attempt(progress, solved, language)` — immutable progress update
- `calculate_user_stats(user_id, repo)` — calculate overall statistics
- `calculate_stats_by_difficulty(user_id, repo, difficulties)` — stats by difficulty

### Drafts Service (`core/services/drafts.py`)

Pure functions for draft management:

- `get_draft(user_id, problem_id, language, repo)` — get existing draft
- `save_draft(user_id, problem_id, language, code, repo)` — save/update draft
- `delete_draft(user_id, problem_id, language, repo)` — delete draft
- `get_or_create_code(user_id, problem_id, language, signature, repo)` — get draft or template

### Module Exports (`core/services/__init__.py`)

All 16 service functions exported with `__all__`.

## Test Results

```
238 passed, 3 warnings in 5.91s
Coverage: ~90%
```

New tests added (69):

- `test_execution.py` — 15 tests (syntax validation, function name extraction)
- `test_problems.py` — 21 tests (get, filter, random, display, examples)
- `test_progress.py` — 18 tests (get, update, stats)
- `test_drafts.py` — 12 tests (get, save, delete, get_or_create)

## Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| Pure functions | No side effects, same input → same output |
| Immutable data | Return new objects, don't modify arguments |
| Dependency injection | Repositories/executors passed as arguments |
| Result type | `Result[T, E]` for operations that can fail |
| Pattern matching | Python 3.10+ `match/case` for Result handling |

## Service Function Signatures

All service functions follow the pattern:
```python
def function_name(
    args...,
    repo: ISomeRepository,  # Dependencies last
) -> Result[T, E] | T:     # Result for fallible, T for infallible
```

## Deviations from Plan

None. Implementation follows the specification.

## Dependencies

```
core/services/ depends on:
  ├── core/domain/models.py (Problem, Progress, Draft, etc.)
  ├── core/domain/enums.py (Difficulty, Language, ProgressStatus)
  ├── core/domain/result.py (Ok, Err, Result)
  ├── core/domain/errors.py (NotFoundError, ValidationError, etc.)
  ├── core/ports/repositories.py (IProblemRepository, etc.)
  └── core/ports/executors.py (ICodeExecutor)
```

## Files Created

```
practiceraptor/
├── core/services/
│   ├── __init__.py        (updated)
│   ├── problems.py        (new)
│   ├── execution.py       (new)
│   ├── progress.py        (new)
│   └── drafts.py          (new)
└── tests/unit/core/services/
    ├── test_problems.py   (new)
    ├── test_execution.py  (new)
    ├── test_progress.py   (new)
    └── test_drafts.py     (new)
```

## Next Step

Proceed to [Step 7: DI Container](./07_di_container.md)
