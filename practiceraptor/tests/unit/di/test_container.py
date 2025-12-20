"""Tests for DI container."""
import pytest
from unittest.mock import MagicMock

from di.container import Container


class TestContainer:
    """Tests for Container class."""

    def test_is_frozen(self) -> None:
        """Container should be immutable."""
        container = Container(
            problem_repo=MagicMock(),
            user_repo=MagicMock(),
            draft_repo=MagicMock(),
            submission_repo=MagicMock(),
            progress_repo=MagicMock(),
            executor=MagicMock(),
            auth=MagicMock(),
        )

        with pytest.raises(AttributeError):
            container.problem_repo = MagicMock()

    def test_holds_all_dependencies(self) -> None:
        """Container holds all required dependencies."""
        problem_repo = MagicMock()
        user_repo = MagicMock()
        draft_repo = MagicMock()
        submission_repo = MagicMock()
        progress_repo = MagicMock()
        executor = MagicMock()
        auth = MagicMock()

        container = Container(
            problem_repo=problem_repo,
            user_repo=user_repo,
            draft_repo=draft_repo,
            submission_repo=submission_repo,
            progress_repo=progress_repo,
            executor=executor,
            auth=auth,
        )

        assert container.problem_repo is problem_repo
        assert container.user_repo is user_repo
        assert container.draft_repo is draft_repo
        assert container.submission_repo is submission_repo
        assert container.progress_repo is progress_repo
        assert container.executor is executor
        assert container.auth is auth

    def test_default_locale(self) -> None:
        """Container has default locale."""
        container = Container(
            problem_repo=MagicMock(),
            user_repo=MagicMock(),
            draft_repo=MagicMock(),
            submission_repo=MagicMock(),
            progress_repo=MagicMock(),
            executor=MagicMock(),
            auth=MagicMock(),
        )

        assert container.default_locale == "en"

    def test_custom_locale(self) -> None:
        """Container accepts custom locale."""
        container = Container(
            problem_repo=MagicMock(),
            user_repo=MagicMock(),
            draft_repo=MagicMock(),
            submission_repo=MagicMock(),
            progress_repo=MagicMock(),
            executor=MagicMock(),
            auth=MagicMock(),
            default_locale="ru",
        )

        assert container.default_locale == "ru"

    def test_default_timeout(self) -> None:
        """Container has default timeout."""
        container = Container(
            problem_repo=MagicMock(),
            user_repo=MagicMock(),
            draft_repo=MagicMock(),
            submission_repo=MagicMock(),
            progress_repo=MagicMock(),
            executor=MagicMock(),
            auth=MagicMock(),
        )

        assert container.default_timeout_sec == 5

    def test_custom_timeout(self) -> None:
        """Container accepts custom timeout."""
        container = Container(
            problem_repo=MagicMock(),
            user_repo=MagicMock(),
            draft_repo=MagicMock(),
            submission_repo=MagicMock(),
            progress_repo=MagicMock(),
            executor=MagicMock(),
            auth=MagicMock(),
            default_timeout_sec=10,
        )

        assert container.default_timeout_sec == 10
