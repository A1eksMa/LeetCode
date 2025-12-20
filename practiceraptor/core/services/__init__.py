"""Service layer - pure functions for business logic."""
from .problems import (
    get_problem,
    get_all_problems,
    filter_problems,
    get_random_problem,
    get_problem_display_text,
    format_examples,
)
from .execution import (
    validate_code_syntax,
    extract_function_name,
    run_tests,
    run_examples_only,
    run_full_tests,
)
from .progress import (
    get_user_progress,
    update_progress_on_attempt,
    calculate_user_stats,
    calculate_stats_by_difficulty,
)
from .drafts import (
    get_draft,
    save_draft,
    delete_draft,
    get_or_create_code,
)

__all__ = [
    # Problems
    "get_problem",
    "get_all_problems",
    "filter_problems",
    "get_random_problem",
    "get_problem_display_text",
    "format_examples",
    # Execution
    "validate_code_syntax",
    "extract_function_name",
    "run_tests",
    "run_examples_only",
    "run_full_tests",
    # Progress
    "get_user_progress",
    "update_progress_on_attempt",
    "calculate_user_stats",
    "calculate_stats_by_difficulty",
    # Drafts
    "get_draft",
    "save_draft",
    "delete_draft",
    "get_or_create_code",
]
