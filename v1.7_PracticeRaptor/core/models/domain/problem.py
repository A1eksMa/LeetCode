"""Problem domain models - rich objects with nested data."""

from dataclasses import dataclass, field

from .enums import Category, Complexity, Difficulty, ProblemStatus, Language, ProgrammingLanguage
from .localization import LocalizedText


@dataclass(frozen=True)
class Example:
    """Problem example with input/output and explanation.

    All data is embedded - no ID references.
    """

    input: str
    output: str
    explanation: LocalizedText = field(default_factory=LocalizedText)


@dataclass(frozen=True)
class ProblemSummary:
    """Lightweight problem data for list display."""

    id: int
    title: LocalizedText
    difficulty: Difficulty
    complexity: Complexity
    categories: tuple[Category, ...]
    tags: tuple[str, ...]
    supported_languages: tuple[Language, ...] = ()
    supported_programming_languages: tuple[ProgrammingLanguage, ...] = ()
    status: ProblemStatus = ProblemStatus.NOT_STARTED


@dataclass(frozen=True)
class Problem:
    """Complete problem with all details.

    Rich domain model with nested objects.
    Loaded when user views a specific problem.

    """

    id: int
    title: LocalizedText
    description: LocalizedText
    difficulty: Difficulty
    complexity: Complexity
    categories: tuple[Category, ...] = ()
    tags: tuple[str, ...] = ()
    examples: tuple[Example, ...] = ()
    hints: tuple[LocalizedText, ...] = ()
    editorial: LocalizedText = field(default_factory=LocalizedText)
    supported_languages: tuple[Language, ...] = ()
    supported_programming_languages: tuple[ProgrammingLanguage, ...] = ()

    def get_title(self, locale: str = "en") -> str:
        """Get title in specified locale."""
        return self.title.get(locale)

    def get_description(self, locale: str = "en") -> str:
        """Get description in specified locale."""
        return self.description.get(locale)

    def supports_programming_language(self, lang: ProgrammingLanguage) -> bool:
        """Check if problem supports given programming language."""
        return lang in self.supported_programming_languages

    def supports_language(self, lang: Language) -> bool:
        """Check if problem supports given language."""
        return lang in self.supported_languages

    def to_summary(self) -> ProblemSummary:
        """Convert to lightweight summary for list display."""
        return ProblemSummary(
            id=self.id,
            title=self.title,
            difficulty=self.difficulty,
            complexity=self.complexity,
            categories=self.categories,
            tags=self.tags,
            supported_languages=self.supported_languages,
            supported_programming_languages=self.supported_programming_languages,
            status=ProblemStatus.NOT_STARTED,
        )
