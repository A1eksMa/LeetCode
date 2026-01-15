"""Problem mapper - Domain ↔ Persistence conversion."""

from dataclasses import dataclass

from core.models.domain.enums import (
    Category,
    Complexity,
    Difficulty,
    Language,
    ProblemStatus,
    ProgrammingLanguage,
)
from core.models.domain.localization import LocalizedText
from core.models.domain.problem import Example, Problem, ProblemSummary

from ..records.problem_records import (
    EditorialRecord,
    ExampleRecord,
    ExplanationRecord,
    HintRecord,
    ProblemRecord,
    TagRecord,
    TitleRecord,
    ProblemDescriptionRecord,
)


# ============================================================
# Helper: Group records by language
# ============================================================


def _group_by_language(records: list, text_field: str) -> LocalizedText:
    """Convert list of localized records to LocalizedText."""
    translations = {r.language: getattr(r, text_field) for r in records}
    return LocalizedText(translations)


def _localized_to_records(
    text: LocalizedText,
    record_class: type,
    id_field: str,
    id_value: int,
    text_field: str,
) -> list:
    """Convert LocalizedText to list of records."""
    return [
        record_class(**{id_field: id_value, "language": lang, text_field: content})
        for lang, content in text.translations.items()
    ]


# ============================================================
# Records → Domain
# ============================================================


def records_to_problem(
    problem_rec: ProblemRecord,
    title_recs: list[TitleRecord],
    description_recs: list[ProblemDescriptionRecord],
    example_recs: list[ExampleRecord],
    explanation_recs: list[ExplanationRecord],
    hint_recs: list[HintRecord],
    tag_recs: list[TagRecord],
    editorial_recs: list[EditorialRecord],
) -> Problem:
    """Assemble Problem domain model from persistence records.

    This is the main entry point for loading a complete problem.
    Repository calls this after fetching all related records.
    """
    # Group explanations by example_id
    explanations_by_example = {}
    for exp in explanation_recs:
        if exp.example_id not in explanations_by_example:
            explanations_by_example[exp.example_id] = []
        explanations_by_example[exp.example_id].append(exp)

    # Build examples with their explanations
    examples = tuple(
        Example(
            input=rec.input,
            output=rec.output,
            explanation=_group_by_language(
                explanations_by_example.get(rec.example_id, []),
                "explanation",
            ),
        )
        for rec in example_recs
    )

    # Group hints by index, then by language
    hints_by_index: dict[int, list[HintRecord]] = {}
    for h in hint_recs:
        if h.hint_index not in hints_by_index:
            hints_by_index[h.hint_index] = []
        hints_by_index[h.hint_index].append(h)

    hints = tuple(
        _group_by_language(hints_by_index[idx], "hint")
        for idx in sorted(hints_by_index.keys())
    )

    return Problem(
        id=problem_rec.id,
        title=_group_by_language(title_recs, "title"),
        description=_group_by_language(description_recs, "description"),
        difficulty=Difficulty(problem_rec.difficulty),
        complexity=Complexity(problem_rec.complexity),
        categories=tuple(Category(c) for c in problem_rec.categories),
        tags=tuple(r.tag for r in tag_recs),
        examples=examples,
        hints=hints,
        editorial=_group_by_language(editorial_recs, "editorial"),
        supported_languages=tuple(
            Language(lang) for lang in problem_rec.supported_languages
        ),
        supported_programming_languages=tuple(
            ProgrammingLanguage(lang) for lang in problem_rec.supported_programming_languages
        ),
    )


def records_to_problem_summary(
    problem_rec: ProblemRecord,
    title_recs: list[TitleRecord],
    tag_recs: list[TagRecord],
    status: ProblemStatus = ProblemStatus.NOT_STARTED,
) -> ProblemSummary:
    """Create lightweight ProblemSummary for list display.

    Only loads essential data - no descriptions, examples, hints.
    """
    return ProblemSummary(
        id=problem_rec.id,
        title=_group_by_language(title_recs, "title"),
        difficulty=Difficulty(problem_rec.difficulty),
        complexity=Complexity(problem_rec.complexity),
        categories=tuple(Category(c) for c in problem_rec.categories),
        tags=tuple(r.tag for r in tag_recs),
        supported_languages=tuple(
            Language(lang) for lang in problem_rec.supported_languages
        ),
        supported_programming_languages=tuple(
            ProgrammingLanguage(lang) for lang in problem_rec.supported_programming_languages
        ),
        status=status,
    )


# ============================================================
# Domain → Records
# ============================================================


@dataclass
class ProblemRecords:
    """Container for all records generated from a Problem."""

    problem: ProblemRecord
    titles: list[TitleRecord]
    descriptions: list[ProblemDescriptionRecord]
    examples: list[ExampleRecord]
    explanations: list[ExplanationRecord]
    hints: list[HintRecord]
    tags: list[TagRecord]
    editorials: list[EditorialRecord]


def problem_to_records(
    problem: Problem,
    example_id_start: int = 1,
) -> ProblemRecords:
    """Decompose Problem domain model into persistence records.

    Args:
        problem: Domain model to convert
        example_id_start: Starting ID for examples (needed for new problems)

    Returns:
        Container with all generated records
    """
    problem_rec = ProblemRecord(
        id=problem.id,
        difficulty=problem.difficulty.value,
        complexity=problem.complexity.value,
        categories=[c.value for c in problem.categories],
        supported_languages=[lang.value for lang in problem.supported_languages],
        supported_programming_languages=[lang.value for lang in problem.supported_programming_languages],
    )

    title_recs = _localized_to_records(
        problem.title, TitleRecord, "problem_id", problem.id, "title"
    )

    description_recs = _localized_to_records(
        problem.description,
        ProblemDescriptionRecord,
        "problem_id",
        problem.id,
        "description",
    )

    # Examples and explanations
    example_recs = []
    explanation_recs = []
    for i, example in enumerate(problem.examples):
        example_id = example_id_start + i
        example_recs.append(
            ExampleRecord(
                example_id=example_id,
                problem_id=problem.id,
                input=example.input,
                output=example.output,
            )
        )
        for lang, text in example.explanation.translations.items():
            explanation_recs.append(
                ExplanationRecord(
                    example_id=example_id,
                    language=lang,
                    explanation=text,
                )
            )

    # Hints (indexed)
    hint_recs = []
    for idx, hint in enumerate(problem.hints):
        for lang, text in hint.translations.items():
            hint_recs.append(
                HintRecord(
                    problem_id=problem.id,
                    language=lang,
                    hint_index=idx,
                    hint=text,
                )
            )

    tag_recs = [TagRecord(problem_id=problem.id, tag=t) for t in problem.tags]

    editorial_recs = _localized_to_records(
        problem.editorial, EditorialRecord, "problem_id", problem.id, "editorial"
    )

    return ProblemRecords(
        problem=problem_rec,
        titles=title_recs,
        descriptions=description_recs,
        examples=example_recs,
        explanations=explanation_recs,
        hints=hint_recs,
        tags=tag_recs,
        editorials=editorial_recs,
    )
