"""Output formatting for CLI."""
from typing import Any

from core.domain.models import Problem, ExecutionResult, TestResult
from core.domain.enums import Difficulty, Language
from core.services import format_examples

from .colors import Colors, SEPARATOR, DOUBLE_SEPARATOR


def display_welcome() -> None:
    """Display welcome banner."""
    banner = f"""
{Colors.CYAN}+========================================+
|       PracticeRaptor CLI               |
+========================================+{Colors.RESET}
"""
    print(banner)


def display_problem_list(problems: tuple[Problem, ...], locale: str = "en") -> None:
    """Display list of available problems."""
    print("\nAvailable problems:")
    print(f"  [{Colors.info('0')}] Random problem")

    for i, problem in enumerate(problems, 1):
        diff_color = _get_difficulty_color(problem.difficulty)
        diff_str = f"{diff_color}{problem.difficulty.value}{Colors.RESET}"
        tags_str = ", ".join(problem.tags)
        title = problem.title.get(locale)

        print(f"  [{i}] {title} ({diff_str}) [{tags_str}]")

    print()


def display_problem(
    problem: Problem,
    language: Language,
    locale: str = "en",
) -> None:
    """Display full problem description."""
    # Header
    print(SEPARATOR)
    print(f"Problem #{problem.id}: {Colors.bold(problem.title.get(locale))}")

    diff_color = _get_difficulty_color(problem.difficulty)
    print(f"Difficulty: {diff_color}{problem.difficulty.value}{Colors.RESET}")
    print(f"Tags: {', '.join(problem.tags)}")
    print(SEPARATOR)

    # Description
    print()
    description = problem.description.get(locale)
    # Handle escaped newlines from JSON
    print(description.replace("\\n", "\n"))

    # Examples
    examples = format_examples(problem, locale)
    for ex in examples:
        print(f"\n{Colors.bold(f'Example {ex[\"number\"]}:')}")
        print(f"  Input: {_format_input(ex['input'])}")
        print(f"  Output: {ex['output']}")
        if "explanation" in ex:
            print(f"  {Colors.muted('Explanation: ' + ex['explanation'])}")

    # Function signature
    lang_spec = problem.get_language_spec(language)
    if lang_spec:
        print(f"\n{Colors.bold('Function signature:')}")
        print(f"  {Colors.info(lang_spec.function_signature)}")

    print()
    print(SEPARATOR)


def display_results(result: ExecutionResult, verbose: bool = False) -> None:
    """Display test execution results."""
    print("\nRunning tests...\n")

    total = result.total_count
    for i, test_result in enumerate(result.test_results, 1):
        _display_test_result(test_result, i, total, verbose)

        if not test_result.passed:
            _display_error_details(test_result)
            print()

    # Summary
    print(DOUBLE_SEPARATOR)
    if result.success:
        print(Colors.success("+ All tests passed!"))
    else:
        print(Colors.error(f"x Tests failed: {result.passed_count}/{result.total_count}"))

    print(f"  Execution time: {result.total_time_ms}ms")
    print(DOUBLE_SEPARATOR)


def display_hint(
    solution_name: str,
    complexity: str,
    code: str,
    index: int,
    total: int,
) -> None:
    """Display a canonical solution as hint."""
    print(f"\n{Colors.warning('=' * 40)}")
    print(Colors.warning(f"Hint {index}/{total}: {solution_name}"))
    print(Colors.muted(f"Complexity: {complexity}"))
    print(Colors.warning("-" * 40))
    print(Colors.info(code))
    print(Colors.warning("=" * 40))
    print()


def display_message(message: str, style: str = "info") -> None:
    """Display a styled message."""
    match style:
        case "success":
            print(Colors.success(message))
        case "error":
            print(Colors.error(message))
        case "warning":
            print(Colors.warning(message))
        case _:
            print(Colors.info(message))


def _get_difficulty_color(difficulty: Difficulty) -> str:
    """Get color for difficulty level."""
    match difficulty:
        case Difficulty.EASY:
            return Colors.GREEN
        case Difficulty.MEDIUM:
            return Colors.YELLOW
        case Difficulty.HARD:
            return Colors.RED
        case _:
            return ""


def _format_input(input_data: dict[str, Any]) -> str:
    """Format input data for display."""
    parts = [f"{k} = {v}" for k, v in input_data.items()]
    return ", ".join(parts)


def _display_test_result(
    result: TestResult,
    test_num: int,
    total: int,
    verbose: bool,
) -> None:
    """Display single test result line."""
    time_str = f"({result.execution_time_ms}ms)"

    if result.passed:
        status_icon = Colors.success("+")
        status_text = "passed"
    elif result.error_message and "timeout" in result.error_message.lower():
        status_icon = Colors.error("x")
        status_text = "timeout"
    elif result.error_message and "Expected" not in result.error_message:
        status_icon = Colors.error("x")
        status_text = "error"
    else:
        status_icon = Colors.error("x")
        status_text = "failed"

    desc = result.test_case.description or ""
    line = f"{status_icon} Test {test_num}/{total}: {status_text} {time_str}"

    if verbose and desc:
        line += f" - {Colors.muted(desc)}"

    print(line)


def _display_error_details(result: TestResult) -> None:
    """Display details for failed test."""
    if result.test_case.description:
        print(f"  {Colors.muted(f'Test: {result.test_case.description}')}")

    if result.error_message:
        if "Expected" in result.error_message:
            # Wrong answer
            print(f"  Input: {Colors.info(str(result.test_case.input))}")
            print(f"  Expected: {Colors.success(str(result.test_case.expected))}")
            print(f"  Actual: {Colors.error(str(result.actual))}")
        else:
            # Runtime error / timeout
            print(f"  {Colors.error(f'Error: {result.error_message}')}")
