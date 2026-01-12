"""Tests for Result type."""
import pytest
from core.domain.result import Ok, Err


class TestOk:
    def test_is_ok_returns_true(self) -> None:
        result = Ok(42)
        assert result.is_ok() is True
        assert result.is_err() is False

    def test_unwrap_returns_value(self) -> None:
        result = Ok("hello")
        assert result.unwrap() == "hello"

    def test_unwrap_or_returns_value(self) -> None:
        result = Ok(42)
        assert result.unwrap_or(0) == 42

    def test_map_applies_function(self) -> None:
        result = Ok(5).map(lambda x: x * 2)
        assert result.unwrap() == 10

    def test_flat_map_chains_results(self) -> None:
        result = Ok(5).flat_map(lambda x: Ok(x * 2))
        assert result.unwrap() == 10

    def test_flat_map_propagates_error(self) -> None:
        result = Ok(5).flat_map(lambda x: Err("error"))
        assert result.is_err()

    def test_repr(self) -> None:
        result = Ok(42)
        assert repr(result) == "Ok(42)"


class TestErr:
    def test_is_err_returns_true(self) -> None:
        result = Err("error")
        assert result.is_err() is True
        assert result.is_ok() is False

    def test_unwrap_raises(self) -> None:
        result = Err("error")
        with pytest.raises(ValueError):
            result.unwrap()

    def test_unwrap_or_returns_default(self) -> None:
        result: Err[str] = Err("error")
        assert result.unwrap_or(42) == 42

    def test_map_propagates_error(self) -> None:
        result = Err("error").map(lambda x: x * 2)
        assert result.is_err()
        assert result.error == "error"

    def test_flat_map_propagates_error(self) -> None:
        result = Err("error").flat_map(lambda x: Ok(x * 2))
        assert result.is_err()
        assert result.error == "error"

    def test_repr(self) -> None:
        result = Err("error")
        assert repr(result) == "Err('error')"
