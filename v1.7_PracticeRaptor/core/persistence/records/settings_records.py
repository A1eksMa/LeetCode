"""User settings persistence records.

Each record corresponds to a JSON file or SQL table.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass


@dataclass
class SettingsRecord:
    """User preferences and current session state.

    Maps to: settings.json / TABLE settings
    Primary key: user_id
    """

    user_id: int = 0 # References UserRecord.user_id

    # Persistent preferences
    language: str = "en" # e.g., "en", "ru"
    programming_language: str = "python3"  # e.g., "python3", "java"
    text_editor: str = "default" # e.g., "default", "vim"

    # Current session state (filters)
    select_problem_id: int | None = None
    select_difficulty: str | None = None  # e.g., "easy", "medium"
    select_tags: list[str] = ()
    select_category: str | None = None  # e.g., "array", "string"
    select_status: str | None = None  # e.g., "solved", "attempted"
