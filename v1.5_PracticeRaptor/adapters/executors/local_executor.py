"""Local code executor using multiprocessing for isolation."""
import ast
import multiprocessing
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from core.domain.models import TestCase, TestResult, ExecutionResult
from core.domain.result import Ok, Err, Result
from core.domain.errors import ExecutionError


@dataclass(frozen=True)
class ExecutorConfig:
    """Configuration for local executor."""

    timeout_sec: int = 5
    memory_limit_mb: int = 256


# Safe builtins whitelist for sandbox environment
SAFE_BUILTINS: dict[str, Any] = {
    # Types
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "frozenset": frozenset,
    "bytes": bytes,
    "bytearray": bytearray,
    "complex": complex,
    "type": type,
    "object": object,
    "slice": slice,
    "range": range,
    # Collection functions
    "len": len,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "reversed": reversed,
    "sorted": sorted,
    # Math functions
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "round": round,
    "divmod": divmod,
    # Logical functions
    "all": all,
    "any": any,
    # Conversions
    "chr": chr,
    "ord": ord,
    "hex": hex,
    "bin": bin,
    "oct": oct,
    "format": format,
    # Object introspection
    "isinstance": isinstance,
    "issubclass": issubclass,
    "hasattr": hasattr,
    "getattr": getattr,
    "callable": callable,
    "iter": iter,
    "next": next,
    "repr": repr,
    "hash": hash,
    "id": id,
    # Constants
    "None": None,
    "True": True,
    "False": False,
    # Exceptions
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "AttributeError": AttributeError,
    "ZeroDivisionError": ZeroDivisionError,
    "StopIteration": StopIteration,
    "RuntimeError": RuntimeError,
}


def _create_sandbox_globals() -> dict[str, Any]:
    """Create restricted globals for code execution."""
    return {
        "__builtins__": SAFE_BUILTINS,
        "__name__": "__main__",
    }


def _execute_in_process(
    code: str,
    test_input: dict[str, Any],
    function_name: str,
    result_queue: "multiprocessing.Queue[dict[str, Any]]",
) -> None:
    """Execute code in separate process for isolation."""
    try:
        sandbox_globals = _create_sandbox_globals()
        sandbox_locals: dict[str, Any] = {}

        # Execute user code
        exec(code, sandbox_globals, sandbox_locals)

        # Check if function exists
        if function_name not in sandbox_locals:
            result_queue.put({
                "success": False,
                "error": f"Function '{function_name}' not found in code",
                "error_type": "runtime",
            })
            return

        func = sandbox_locals[function_name]

        # Deep copy inputs to prevent mutation
        inputs = deepcopy(test_input)

        # Execute function with keyword arguments
        start_time = time.perf_counter()
        actual = func(**inputs)
        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        result_queue.put({
            "success": True,
            "actual": actual,
            "execution_time_ms": execution_time_ms,
        })

    except SyntaxError as e:
        result_queue.put({
            "success": False,
            "error": f"Syntax error: {e}",
            "error_type": "syntax",
        })
    except Exception as e:
        result_queue.put({
            "success": False,
            "error": f"{type(e).__name__}: {e}",
            "error_type": "runtime",
        })


class LocalExecutor:
    """Local code executor using multiprocessing for isolation."""

    def __init__(self, config: ExecutorConfig | None = None) -> None:
        self.config = config or ExecutorConfig()

    def validate_syntax(self, code: str) -> Result[None, ExecutionError]:
        """Check if code has valid Python syntax."""
        try:
            ast.parse(code)
            return Ok(None)
        except SyntaxError as e:
            return Err(ExecutionError(
                message=f"Line {e.lineno}: {e.msg}",
                error_type="syntax",
            ))

    def execute(
        self,
        code: str,
        test_cases: tuple[TestCase, ...],
        function_name: str,
        timeout_sec: int | None = None,
    ) -> Result[ExecutionResult, ExecutionError]:
        """Execute code against test cases."""
        # Validate syntax first
        syntax_result = self.validate_syntax(code)
        if syntax_result.is_err():
            return Err(syntax_result.error)

        timeout = timeout_sec if timeout_sec is not None else self.config.timeout_sec
        test_results: list[TestResult] = []
        total_time_ms = 0
        all_passed = True

        for test_case in test_cases:
            result = self._run_single_test(code, test_case, function_name, timeout)

            if result.is_err():
                return Err(result.error)

            test_result = result.unwrap()
            test_results.append(test_result)
            total_time_ms += test_result.execution_time_ms

            if not test_result.passed:
                all_passed = False
                break  # Stop on first failure

        return Ok(ExecutionResult(
            success=all_passed,
            test_results=tuple(test_results),
            total_time_ms=total_time_ms,
        ))

    def _run_single_test(
        self,
        code: str,
        test_case: TestCase,
        function_name: str,
        timeout_sec: int,
    ) -> Result[TestResult, ExecutionError]:
        """Run a single test case."""
        result_queue: "multiprocessing.Queue[dict[str, Any]]" = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_execute_in_process,
            args=(code, test_case.input, function_name, result_queue),
        )

        process.start()
        process.join(timeout=timeout_sec)

        if process.is_alive():
            # Timeout - terminate process
            process.terminate()
            process.join(timeout=1)

            # Force kill if still alive
            if process.is_alive():
                process.kill()
                process.join()

            return Ok(TestResult(
                test_case=test_case,
                passed=False,
                error_message=f"Timeout: exceeded {timeout_sec}s",
            ))

        if result_queue.empty():
            return Err(ExecutionError(
                message="Process terminated unexpectedly",
                error_type="runtime",
            ))

        result_data = result_queue.get()

        if not result_data["success"]:
            return Ok(TestResult(
                test_case=test_case,
                passed=False,
                error_message=result_data["error"],
            ))

        actual = result_data["actual"]
        passed = self._compare_results(actual, test_case.expected)

        error_message = None
        if not passed:
            error_message = f"Expected {test_case.expected}, got {actual}"

        return Ok(TestResult(
            test_case=test_case,
            passed=passed,
            actual=actual,
            execution_time_ms=result_data["execution_time_ms"],
            error_message=error_message,
        ))

    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected results with type-aware comparison."""
        # Handle float comparison with tolerance
        if isinstance(actual, float) and isinstance(expected, float):
            return abs(actual - expected) < 1e-9

        # Handle list/tuple comparison
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                return False
            return all(
                self._compare_results(a, e)
                for a, e in zip(actual, expected)
            )

        # Handle dict comparison
        if isinstance(actual, dict) and isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            return all(
                self._compare_results(actual[k], expected[k])
                for k in actual
            )

        # Direct comparison
        return actual == expected
