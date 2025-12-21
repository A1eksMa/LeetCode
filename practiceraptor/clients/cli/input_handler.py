"""User input handling for CLI."""
from dataclasses import dataclass

from core.domain.models import Problem
from core.domain.enums import Language

from .colors import Colors
from .presenter import display_hint


@dataclass
class InputResult:
    """Result of user code input."""

    code: str | None = None
    cancelled: bool = False


def get_user_choice(min_val: int, max_val: int, prompt: str = "Choose") -> int:
    """Get numeric choice from user."""
    while True:
        try:
            user_input = input(f"{prompt} ({min_val}-{max_val}): ").strip()
            value = int(user_input)

            if min_val <= value <= max_val:
                return value
            else:
                print(Colors.error(f"Enter a number from {min_val} to {max_val}"))
        except ValueError:
            print(Colors.error("Enter a number"))


def read_user_code(
    problem: Problem,
    language: Language,
    previous_code: str | None = None,
) -> InputResult:
    """
    Read multiline code from user.

    Supports commands:
    - !hint: Show canonical solution
    - !reset: Clear entered code
    - !cancel: Cancel and return to menu

    Input ends with double Enter (two empty lines).
    """
    hint_index = 0
    lang_spec = problem.get_language_spec(language)
    solutions = lang_spec.solutions if lang_spec else ()

    # Show previous code if any
    if previous_code:
        _show_previous_code(previous_code)

    print("Enter your solution (double Enter to submit, !hint for help):")

    lines: list[str] = []
    empty_count = 0

    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break

        # Check commands
        stripped = line.strip().lower()

        if stripped == "!hint":
            if solutions and hint_index < len(solutions):
                sol = solutions[hint_index]
                display_hint(sol.name, sol.complexity, sol.code, hint_index + 1, len(solutions))
                hint_index += 1
            elif not solutions:
                print(Colors.warning("\nNo hints available for this problem.\n"))
            else:
                print(Colors.warning("\nNo more hints.\n"))
            continue

        if stripped == "!reset":
            lines = []
            empty_count = 0
            print(Colors.info("Code cleared. Enter again:"))
            continue

        if stripped == "!cancel":
            return InputResult(cancelled=True)

        # Handle empty lines
        if not line.strip():
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append("")
        else:
            empty_count = 0
            lines.append(line)

    # Remove trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    code = "\n".join(lines)

    if not code.strip():
        return InputResult(cancelled=True)

    return InputResult(code=code)


def read_code_from_file(file_path: str) -> str:
    """Read code from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def ask_continue() -> bool:
    """Ask user if they want to continue."""
    while True:
        answer = input("\nContinue? (y/n): ").strip().lower()
        if answer in ("y", "yes", ""):
            return True
        if answer in ("n", "no"):
            return False
        print("Enter y or n")


def ask_retry() -> bool:
    """Ask user if they want to retry."""
    answer = input("\nTry again? (y/n): ").strip().lower()
    return answer in ("y", "yes", "")


def _show_previous_code(code: str) -> None:
    """Display previous code for reference."""
    print(Colors.muted("\nPrevious code:"))
    print(Colors.muted("+" + "-" * 38))
    for line in code.split("\n"):
        print(Colors.muted(f"| {line}"))
    print(Colors.muted("+" + "-" * 38))
    print()
