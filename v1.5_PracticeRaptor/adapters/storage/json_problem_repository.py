"""JSON implementation of IProblemRepository."""
from pathlib import Path
from typing import Any

from core.domain.models import (
    Problem,
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
)
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError

from .json_base import JsonStorageBase


class JsonProblemRepository(JsonStorageBase[Problem]):
    """JSON file-based problem repository."""

    def __init__(self, problems_path: Path):
        super().__init__(problems_path)
        self._cache: dict[int, Problem] | None = None

    def _load_all(self) -> dict[int, Problem]:
        """Load all problems from files (with caching)."""
        if self._cache is not None:
            return self._cache

        problems: dict[int, Problem] = {}
        for file_path in self.base_path.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                problem = self._parse_problem(result.unwrap())
                if problem:
                    problems[problem.id] = problem

        self._cache = problems
        return problems

    def _parse_problem(self, data: dict[str, Any]) -> Problem | None:
        """Parse JSON to Problem model."""
        try:
            # Parse localized text fields
            title = self._parse_localized(data.get("title", {}))
            description = self._parse_localized(data.get("description", {}))

            # Parse examples
            examples = tuple(
                Example(
                    input=ex["input"],
                    output=ex["output"],
                    explanation=self._parse_localized(ex.get("explanation"))
                    if ex.get("explanation") else None,
                )
                for ex in data.get("examples", [])
            )

            # Parse test cases
            test_cases = tuple(
                TestCase(
                    input=tc["input"],
                    expected=tc["expected"],
                    description=tc.get("description"),
                    is_hidden=tc.get("is_hidden", False),
                )
                for tc in data.get("test_cases", [])
            )

            # Parse language specs
            languages: list[LanguageSpec] = []

            # New format: languages dict
            for lang_key, lang_data in data.get("languages", {}).items():
                if lang_key in ("python3", "go", "java", "javascript"):
                    lang_enum = Language(lang_key)
                    solutions = tuple(
                        Solution(
                            name=s["name"],
                            complexity=s["complexity"],
                            code=s["code"],
                        )
                        for s in lang_data.get("solutions", [])
                    )
                    languages.append(LanguageSpec(
                        language=lang_enum,
                        function_signature=lang_data["function_signature"],
                        solutions=solutions,
                    ))

            # Support old format (python3 at root level)
            if "python3" in data and "languages" not in data:
                lang_data = data["python3"]
                solutions = tuple(
                    Solution(
                        name=s["name"],
                        complexity=s["complexity"],
                        code=s["code"],
                    )
                    for s in lang_data.get("solutions", [])
                )
                languages.append(LanguageSpec(
                    language=Language.PYTHON,
                    function_signature=lang_data["function_signature"],
                    solutions=solutions,
                ))

            # Parse hints
            hints = tuple(
                self._parse_localized(h) for h in data.get("hints", [])
            )

            return Problem(
                id=data["id"],
                title=title,
                description=description,
                difficulty=Difficulty(data["difficulty"]),
                tags=tuple(data.get("tags", [])),
                examples=examples,
                test_cases=test_cases,
                languages=tuple(languages),
                hints=hints,
            )
        except (KeyError, ValueError):
            return None

    def _parse_localized(self, data: str | dict[str, str] | None) -> LocalizedText:
        """Parse localized text (supports string or dict)."""
        if data is None:
            return LocalizedText({})
        if isinstance(data, str):
            return LocalizedText({"en": data})
        return LocalizedText(data)

    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
        """Get problem by ID."""
        problems = self._load_all()
        if problem_id in problems:
            return Ok(problems[problem_id])
        return Err(NotFoundError(
            entity="Problem",
            id=problem_id,
        ))

    def get_all(self) -> tuple[Problem, ...]:
        """Get all problems."""
        problems = self._load_all()
        return tuple(sorted(problems.values(), key=lambda p: p.id))

    def filter(
        self,
        difficulty: Difficulty | None = None,
        tags: tuple[str, ...] | None = None,
        language: Language | None = None,
    ) -> tuple[Problem, ...]:
        """Filter problems by criteria."""
        problems = list(self.get_all())

        if difficulty:
            problems = [p for p in problems if p.difficulty == difficulty]

        if tags:
            problems = [
                p for p in problems
                if any(tag in p.tags for tag in tags)
            ]

        if language:
            problems = [
                p for p in problems
                if p.get_language_spec(language) is not None
            ]

        return tuple(problems)

    def count(self) -> int:
        """Get total number of problems."""
        return len(self._load_all())

    def invalidate_cache(self) -> None:
        """Clear the cache to reload from files."""
        self._cache = None
