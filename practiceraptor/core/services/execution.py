"""Code execution pure functions."""
import ast
import re

from core.domain.models import Problem, TestCase, ExecutionResult
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import ValidationError, ExecutionError
from core.ports.executors import ICodeExecutor


def validate_code_syntax(code: str) -> Result[str, ValidationError]:
    """Validate Python code syntax."""
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


def extract_function_name(signature: str) -> str:
    """Extract function name from signature."""
    # "def two_sum(nums: list[int], target: int) -> list[int]:"
    match = re.match(r'def\s+(\w+)\s*\(', signature)
    if match:
        return match.group(1)
    return "solution"


def run_tests(
    code: str,
    test_cases: tuple[TestCase, ...],
    function_name: str,
    executor: ICodeExecutor,
    timeout_sec: int = 5,
) -> Result[ExecutionResult, ExecutionError]:
    """Run code against test cases."""
    return executor.execute(
        code=code,
        test_cases=test_cases,
        function_name=function_name,
        timeout_sec=timeout_sec,
    )


def run_examples_only(
    code: str,
    problem: Problem,
    language: Language,
    executor: ICodeExecutor,
) -> Result[ExecutionResult, ExecutionError]:
    """Run code against example test cases only (quick check)."""
    lang_spec = problem.get_language_spec(language)
    if not lang_spec:
        return Err(ExecutionError(
            message=f"Language {language.value} not supported for this problem",
            error_type="validation",
        ))

    # Convert examples to test cases
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


def run_full_tests(
    code: str,
    problem: Problem,
    language: Language,
    executor: ICodeExecutor,
) -> Result[ExecutionResult, ExecutionError]:
    """Run code against all test cases."""
    lang_spec = problem.get_language_spec(language)
    if not lang_spec:
        return Err(ExecutionError(
            message=f"Language {language.value} not supported for this problem",
            error_type="validation",
        ))

    function_name = extract_function_name(lang_spec.function_signature)

    return run_tests(code, problem.test_cases, function_name, executor)
