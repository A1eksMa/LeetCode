"""User settings domain model."""

from dataclasses import dataclass

from .enums import (
    Category,
    Difficulty,
    Language,
    ProgrammingLanguage,
    ProblemStatus,
    TextEditor,
)


@dataclass(frozen=True)
class Settings:
    """User preferences and current session state.

    Contains both persistent preferences (language, editor)
    and ephemeral session state (current filters and selection).
    """

    user_id: int = 0

    # Persistent preferences
    language: Language = Language.EN
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON
    text_editor: TextEditor = TextEditor.DEFAULT

    # Current session state (filters)
    select_problem_id: int | None = None
    select_difficulty: Difficulty | None = None
    select_tags: tuple[str, ...] = ()
    select_category: Category | None = None
    select_status: ProblemStatus | None = None


# Default settings for new users
DEFAULT_SETTINGS = Settings(
    user_id=0,
    language=Language.EN,
    programming_language=ProgrammingLanguage.PYTHON,
    text_editor=TextEditor.DEFAULT,
)
