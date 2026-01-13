"""Localized content domain models.

All multilingual content is stored as separate records
(normalized) rather than nested dictionaries.
This enables efficient database queries by language.
"""

from dataclasses import dataclass

from .enums import Language


@dataclass(frozen=True)
class Title:
    """Localized problem title."""

    problem_id: int
    language: Language
    title: str = ""


@dataclass(frozen=True)
class Description:
    """Localized problem description."""

    problem_id: int
    language: Language
    description: str = ""


@dataclass(frozen=True)
class Editorial:
    """Localized problem editorial (solution explanation)."""

    problem_id: int
    language: Language
    editorial: str = ""


@dataclass(frozen=True)
class Explanation:
    """Localized example explanation."""

    example_id: int
    language: Language
    explanation: str = ""


@dataclass(frozen=True)
class Hint:
    """Localized problem hint."""

    problem_id: int
    language: Language
    hint: str = ""


@dataclass(frozen=True)
class Tag:
    """Problem tag (flexible labeling system).

    Unlike Category (enum), tags are free-form strings
    for organic growth and community tagging.
    """

    problem_id: int
    tag: str = ""
