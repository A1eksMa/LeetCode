"""Tests for anonymous authentication provider."""
import pytest

from adapters.auth.anonymous_auth import AnonymousAuthProvider
from core.domain.enums import Language


class TestAnonymousAuthProvider:
    """Tests for AnonymousAuthProvider class."""

    def test_get_current_user_returns_ok(self) -> None:
        """get_current_user should return Ok with user."""
        provider = AnonymousAuthProvider()

        result = provider.get_current_user()

        assert result.is_ok()

    def test_user_has_id(self) -> None:
        """User should have an ID."""
        provider = AnonymousAuthProvider()

        result = provider.get_current_user()
        user = result.unwrap()

        assert user.id is not None
        assert len(user.id) > 0

    def test_user_id_starts_with_local(self) -> None:
        """Auto-generated user ID should start with 'local_'."""
        provider = AnonymousAuthProvider()

        result = provider.get_current_user()
        user = result.unwrap()

        assert user.id.startswith("local_")

    def test_custom_user_id(self) -> None:
        """Provider should use custom user ID if provided."""
        provider = AnonymousAuthProvider(user_id="custom_user_123")

        result = provider.get_current_user()
        user = result.unwrap()

        assert user.id == "custom_user_123"

    def test_user_has_locale(self) -> None:
        """User should have English locale by default."""
        provider = AnonymousAuthProvider()

        result = provider.get_current_user()
        user = result.unwrap()

        assert user.locale == "en"

    def test_user_has_preferred_language(self) -> None:
        """User should have Python as preferred language."""
        provider = AnonymousAuthProvider()

        result = provider.get_current_user()
        user = result.unwrap()

        assert user.preferred_language == Language.PYTHON

    def test_user_has_created_at(self) -> None:
        """User should have created_at timestamp."""
        provider = AnonymousAuthProvider()

        result = provider.get_current_user()
        user = result.unwrap()

        assert user.created_at is not None

    def test_same_user_returned(self) -> None:
        """Same user should be returned on multiple calls."""
        provider = AnonymousAuthProvider()

        user1 = provider.get_current_user().unwrap()
        user2 = provider.get_current_user().unwrap()

        assert user1 is user2

    def test_authenticate_returns_current_user(self) -> None:
        """authenticate should return current user ignoring credentials."""
        provider = AnonymousAuthProvider()

        result = provider.authenticate({"username": "ignored", "password": "ignored"})

        assert result.is_ok()
        assert result.unwrap() == provider.get_current_user().unwrap()

    def test_authenticate_with_empty_credentials(self) -> None:
        """authenticate should work with empty credentials."""
        provider = AnonymousAuthProvider()

        result = provider.authenticate({})

        assert result.is_ok()

    def test_different_providers_have_different_ids(self) -> None:
        """Different provider instances should have different user IDs."""
        provider1 = AnonymousAuthProvider()
        provider2 = AnonymousAuthProvider()

        user1 = provider1.get_current_user().unwrap()
        user2 = provider2.get_current_user().unwrap()

        assert user1.id != user2.id
