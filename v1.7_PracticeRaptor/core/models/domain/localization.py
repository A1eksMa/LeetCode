"""Localization support for domain models."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LocalizedText:
    """Multi-language text with fallback support.

    Stores translations as a dictionary and provides
    convenient access with automatic fallback.

    Example:
        title = LocalizedText({"en": "Two Sum", "ru": "Два числа"})
        title.get("ru")  # → "Два числа"
        title.get("de")  # → "Two Sum" (fallback to en)
    """

    translations: dict[str, str] = field(default_factory=dict)

    def get(self, locale: str, fallback: str = "en") -> str:
        """Get text for locale with fallback."""
        return self.translations.get(locale, self.translations.get(fallback, ""))

    def __str__(self) -> str:
        """Default string representation (English)."""
        return self.get("en")

    def __bool__(self) -> bool:
        """Check if any translations exist."""
        return bool(self.translations)


# Convenience constructor for single-language text
def text(en: str, ru: str = "") -> LocalizedText:
    """Create LocalizedText with English and optional Russian."""
    translations = {"en": en}
    if ru:
        translations["ru"] = ru
    return LocalizedText(translations)
