"""Solution mapper - Domain ↔ Persistence conversion."""

from dataclasses import dataclass

from core.models.domain.enums import Complexity, ProgrammingLanguage
from core.models.domain.solution import CanonicalSolution, Signature, Solution, TestCase

from ..records.solution_records import (
    CanonicalSolutionRecord,
    SignatureRecord,
    TestCaseRecord,
)


# ============================================================
# Records → Domain
# ============================================================


def records_to_solution(
    problem_id: int,
    language: ProgrammingLanguage,
    signature_rec: SignatureRecord,
    test_case_recs: list[TestCaseRecord],
    canonical_solution_recs: list[CanonicalSolutionRecord],
) -> Solution:
    """Assemble Solution domain model from persistence records.

    Args:
        problem_id: Problem ID
        language: Programming language for this solution
        signature_rec: Function signature record
        test_case_recs: Test cases for this language
        canonical_solution_recs: Reference solutions for this language

    Returns:
        Complete Solution ready for problem solving
    """
    signature = Signature(
        language=ProgrammingLanguage(signature_rec.programming_language),
        signature=signature_rec.signature,
    )

    test_cases = tuple(
        TestCase(
            language=ProgrammingLanguage(rec.programming_language),
            test=rec.test,
            is_example=rec.is_example,
        )
        for rec in test_case_recs
    )

    canonical_solutions = tuple(
        CanonicalSolution(
            language=ProgrammingLanguage(rec.programming_language),
            name=rec.name,
            complexity=Complexity(rec.complexity),
            code=rec.code,
        )
        for rec in canonical_solution_recs
    )

    return Solution(
        problem_id=problem_id,
        language=language,
        signature=signature,
        test_cases=test_cases,
        canonical_solutions=canonical_solutions,
        code="",  # Empty - user fills during solving
    )


# ============================================================
# Domain → Records
# ============================================================


@dataclass
class SolutionRecords:
    """Container for all records generated from a Solution."""

    signature: SignatureRecord
    test_cases: list[TestCaseRecord]
    canonical_solutions: list[CanonicalSolutionRecord]


def solution_to_records(
    problem_id: int,
    solution: Solution,
    test_case_id_start: int = 1,
    canonical_solution_id_start: int = 1,
) -> SolutionRecords:
    """Decompose Solution domain model into persistence records.

    Note: This is typically used when creating new problems.
    For user solutions, only the code is saved (as Draft or Submission).
    """
    signature_rec = SignatureRecord(
        problem_id=problem_id,
        programming_language=solution.language.value,
        signature=solution.signature.signature,
    )

    test_case_recs = [
        TestCaseRecord(
            test_case_id=test_case_id_start + i,
            problem_id=problem_id,
            programming_language=tc.language.value,
            test=tc.test,
            is_example=tc.is_example,
        )
        for i, tc in enumerate(solution.test_cases)
    ]

    canonical_solution_recs = [
        CanonicalSolutionRecord(
            canonical_solution_id=canonical_solution_id_start + i,
            problem_id=problem_id,
            programming_language=cs.language.value,
            name=cs.name,
            complexity=cs.complexity.value,
            code=cs.code,
        )
        for i, cs in enumerate(solution.canonical_solutions)
    ]

    return SolutionRecords(
        signature=signature_rec,
        test_cases=test_case_recs,
        canonical_solutions=canonical_solution_recs,
    )
