"""Main CLI application class."""
import random

from core.domain.models import Problem
from core.domain.enums import Language
from core.domain.result import Ok, Err
from core.services import (
    get_all_problems,
    validate_code_syntax,
    run_full_tests,
)
from di import Container

from .presenter import (
    display_welcome,
    display_problem_list,
    display_problem,
    display_results,
    display_message,
)
from .input_handler import (
    get_user_choice,
    read_user_code,
    read_code_from_file,
    ask_continue,
    ask_retry,
)


class CLIApp:
    """
    Main CLI application.

    Orchestrates the problem-solving flow using core services
    and dependencies from the DI container.
    """

    def __init__(self, container: Container) -> None:
        self.container = container
        self.locale = container.default_locale
        self.language = Language.PYTHON

    def run(
        self,
        task_id: int | None = None,
        file_path: str | None = None,
        verbose: bool = False,
    ) -> int:
        """
        Run the CLI application.

        Args:
            task_id: Optional problem ID to jump to
            file_path: Optional file with solution code
            verbose: Show verbose output

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        # Load problems
        problems = get_all_problems(self.container.problem_repo)

        if not problems:
            display_message("No problems found", "error")
            return 1

        display_welcome()

        # Handle file mode
        if file_path:
            return self._run_file_mode(problems, task_id, file_path, verbose)

        # Handle direct task mode
        if task_id:
            return self._run_single_task(problems, task_id, verbose)

        # Interactive mode
        return self._run_interactive(problems, verbose)

    def _run_file_mode(
        self,
        problems: tuple[Problem, ...],
        task_id: int | None,
        file_path: str,
        verbose: bool,
    ) -> int:
        """Run with code from file."""
        try:
            code = read_code_from_file(file_path)
        except FileNotFoundError:
            display_message(f"File not found: {file_path}", "error")
            return 1

        if task_id:
            problem = self._get_problem_by_index(problems, task_id)
            if not problem:
                display_message(f"Problem #{task_id} not found", "error")
                return 1
        else:
            problem = self._select_problem(problems)

        return self._solve_with_code(problem, code, verbose)

    def _run_single_task(
        self,
        problems: tuple[Problem, ...],
        task_id: int,
        verbose: bool,
    ) -> int:
        """Run single task by ID."""
        problem = self._get_problem_by_index(problems, task_id)
        if not problem:
            display_message(f"Problem #{task_id} not found", "error")
            return 1

        success = self._solve_problem(problem, verbose)
        return 0 if success else 1

    def _run_interactive(
        self,
        problems: tuple[Problem, ...],
        verbose: bool,
    ) -> int:
        """Run interactive mode."""
        while True:
            try:
                problem = self._select_problem(problems)
                self._solve_problem(problem, verbose)

                if not ask_continue():
                    break

            except KeyboardInterrupt:
                print("\n")
                break

        display_message("\nGoodbye!", "info")
        return 0

    def _select_problem(self, problems: tuple[Problem, ...]) -> Problem:
        """Display problem list and get user selection."""
        display_problem_list(problems, self.locale)

        choice = get_user_choice(0, len(problems))

        if choice == 0:
            problem = random.choice(problems)
            display_message(
                f"\nRandom problem: {problem.title.get(self.locale)}",
                "info",
            )
            return problem

        return problems[choice - 1]

    def _get_problem_by_index(
        self,
        problems: tuple[Problem, ...],
        index: int,
    ) -> Problem | None:
        """Get problem by 1-based index."""
        if 1 <= index <= len(problems):
            return problems[index - 1]
        return None

    def _solve_problem(self, problem: Problem, verbose: bool) -> bool:
        """
        Full problem solving flow.

        Returns True if solved successfully.
        """
        display_problem(problem, self.language, self.locale)

        previous_code: str | None = None

        while True:
            # Get code from user
            result = read_user_code(problem, self.language, previous_code)

            if result.cancelled:
                display_message("\nCancelled.", "warning")
                return False

            code = result.code
            if code is None:
                display_message("\nCancelled.", "warning")
                return False

            # Validate syntax
            syntax_result = validate_code_syntax(code)
            if syntax_result.is_err():
                error = syntax_result.unwrap_err()
                display_message(f"\nx Syntax error: {error.message}", "error")
                display_message("Try again.", "warning")
                previous_code = code
                continue

            # Run tests
            success = self._run_and_display_results(problem, code, verbose)

            if success:
                return True

            # Ask to retry
            if not ask_retry():
                return False

            previous_code = code

    def _solve_with_code(
        self,
        problem: Problem,
        code: str,
        verbose: bool,
    ) -> int:
        """Solve with provided code (file mode)."""
        display_problem(problem, self.language, self.locale)

        # Validate syntax
        syntax_result = validate_code_syntax(code)
        if syntax_result.is_err():
            error = syntax_result.unwrap_err()
            display_message(f"\nx Syntax error: {error.message}", "error")
            return 1

        success = self._run_and_display_results(problem, code, verbose)
        return 0 if success else 1

    def _run_and_display_results(
        self,
        problem: Problem,
        code: str,
        verbose: bool,
    ) -> bool:
        """Run tests and display results."""
        result = run_full_tests(
            code=code,
            problem=problem,
            language=self.language,
            executor=self.container.executor,
        )

        match result:
            case Ok(exec_result):
                display_results(exec_result, verbose)
                return exec_result.success
            case Err(error):
                display_message(f"\nx Execution error: {error.message}", "error")
                return False
