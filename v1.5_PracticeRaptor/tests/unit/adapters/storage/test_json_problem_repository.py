"""Tests for JsonProblemRepository."""
import json
import pytest
from pathlib import Path

from adapters.storage.json_problem_repository import JsonProblemRepository
from core.domain.enums import Difficulty, Language


@pytest.fixture
def sample_problem_json() -> dict:
    """Return sample problem JSON data."""
    return {
        "id": 1,
        "title": {"en": "Two Sum", "ru": "Сумма двух"},
        "description": {"en": "Given an array of integers..."},
        "difficulty": "easy",
        "tags": ["array", "hash-table"],
        "examples": [
            {
                "input": {"nums": [2, 7, 11, 15], "target": 9},
                "output": [0, 1],
                "explanation": {"en": "Because nums[0] + nums[1] == 9."},
            }
        ],
        "test_cases": [
            {
                "input": {"nums": [2, 7, 11, 15], "target": 9},
                "expected": [0, 1],
                "description": "Basic test",
                "is_hidden": False,
            },
            {
                "input": {"nums": [3, 2, 4], "target": 6},
                "expected": [1, 2],
                "is_hidden": True,
            },
        ],
        "languages": {
            "python3": {
                "function_signature": "def two_sum(nums: list[int], target: int) -> list[int]:",
                "solutions": [
                    {
                        "name": "Hash Map",
                        "complexity": "O(n)",
                        "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i",
                    }
                ],
            }
        },
        "hints": [
            {"en": "Think about using a hash map."},
        ],
    }


@pytest.fixture
def sample_problem_old_format() -> dict:
    """Return sample problem in old format (python3 at root)."""
    return {
        "id": 2,
        "title": "Reverse String",
        "description": "Write a function that reverses a string.",
        "difficulty": "easy",
        "tags": ["string"],
        "examples": [
            {"input": {"s": "hello"}, "output": "olleh"}
        ],
        "test_cases": [
            {"input": {"s": "hello"}, "expected": "olleh"}
        ],
        "python3": {
            "function_signature": "def reverse_string(s: str) -> str:",
            "solutions": [],
        },
        "hints": [],
    }


class TestJsonProblemRepository:
    """Tests for JsonProblemRepository."""

    def test_get_by_id_returns_problem(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test getting a problem by ID."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        repo = JsonProblemRepository(tmp_path)

        result = repo.get_by_id(1)

        assert result.is_ok()
        problem = result.unwrap()
        assert problem.id == 1
        assert problem.title.get("en") == "Two Sum"
        assert problem.title.get("ru") == "Сумма двух"
        assert problem.difficulty == Difficulty.EASY
        assert "array" in problem.tags
        assert len(problem.examples) == 1
        assert len(problem.test_cases) == 2

    def test_get_by_id_returns_error_for_missing(self, tmp_path: Path) -> None:
        """Test that getting a missing problem returns an error."""
        repo = JsonProblemRepository(tmp_path)

        result = repo.get_by_id(999)

        assert result.is_err()
        assert result.error.entity == "Problem"

    def test_get_all_returns_all_problems(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test getting all problems."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        problem2 = sample_problem_json.copy()
        problem2["id"] = 2
        problem2["title"] = {"en": "Second Problem"}
        (tmp_path / "2.json").write_text(json.dumps(problem2))
        repo = JsonProblemRepository(tmp_path)

        problems = repo.get_all()

        assert len(problems) == 2
        assert problems[0].id == 1
        assert problems[1].id == 2

    def test_filter_by_difficulty(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test filtering problems by difficulty."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        medium_problem = sample_problem_json.copy()
        medium_problem["id"] = 2
        medium_problem["difficulty"] = "medium"
        (tmp_path / "2.json").write_text(json.dumps(medium_problem))
        repo = JsonProblemRepository(tmp_path)

        easy_problems = repo.filter(difficulty=Difficulty.EASY)
        medium_problems = repo.filter(difficulty=Difficulty.MEDIUM)

        assert len(easy_problems) == 1
        assert easy_problems[0].difficulty == Difficulty.EASY
        assert len(medium_problems) == 1
        assert medium_problems[0].difficulty == Difficulty.MEDIUM

    def test_filter_by_tags(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test filtering problems by tags."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        repo = JsonProblemRepository(tmp_path)

        array_problems = repo.filter(tags=("array",))
        string_problems = repo.filter(tags=("string",))

        assert len(array_problems) == 1
        assert len(string_problems) == 0

    def test_filter_by_language(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test filtering problems by language."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        repo = JsonProblemRepository(tmp_path)

        python_problems = repo.filter(language=Language.PYTHON)
        go_problems = repo.filter(language=Language.GO)

        assert len(python_problems) == 1
        assert len(go_problems) == 0

    def test_count_returns_number_of_problems(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test counting problems."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        problem2 = sample_problem_json.copy()
        problem2["id"] = 2
        (tmp_path / "2.json").write_text(json.dumps(problem2))
        repo = JsonProblemRepository(tmp_path)

        count = repo.count()

        assert count == 2

    def test_invalidate_cache_reloads_from_files(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test that invalidating cache reloads problems."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        repo = JsonProblemRepository(tmp_path)

        # Load initial problems
        assert repo.count() == 1

        # Add a new problem file
        problem2 = sample_problem_json.copy()
        problem2["id"] = 2
        (tmp_path / "2.json").write_text(json.dumps(problem2))

        # Cache still has old data
        assert repo.count() == 1

        # Invalidate and reload
        repo.invalidate_cache()
        assert repo.count() == 2

    def test_parses_old_format(
        self, tmp_path: Path, sample_problem_old_format: dict
    ) -> None:
        """Test parsing problems in old format (python3 at root)."""
        (tmp_path / "2.json").write_text(json.dumps(sample_problem_old_format))
        repo = JsonProblemRepository(tmp_path)

        result = repo.get_by_id(2)

        assert result.is_ok()
        problem = result.unwrap()
        assert problem.id == 2
        assert problem.title.get("en") == "Reverse String"
        lang_spec = problem.get_language_spec(Language.PYTHON)
        assert lang_spec is not None
        assert "reverse_string" in lang_spec.function_signature

    def test_skips_malformed_files(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test that malformed files are skipped."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        (tmp_path / "bad.json").write_text('{"id": "not a number"}')
        repo = JsonProblemRepository(tmp_path)

        problems = repo.get_all()

        assert len(problems) == 1
        assert problems[0].id == 1

    def test_parses_language_spec_with_solutions(
        self, tmp_path: Path, sample_problem_json: dict
    ) -> None:
        """Test that language specs with solutions are parsed correctly."""
        (tmp_path / "1.json").write_text(json.dumps(sample_problem_json))
        repo = JsonProblemRepository(tmp_path)

        result = repo.get_by_id(1)

        assert result.is_ok()
        problem = result.unwrap()
        lang_spec = problem.get_language_spec(Language.PYTHON)
        assert lang_spec is not None
        assert len(lang_spec.solutions) == 1
        assert lang_spec.solutions[0].name == "Hash Map"
        assert lang_spec.solutions[0].complexity == "O(n)"
