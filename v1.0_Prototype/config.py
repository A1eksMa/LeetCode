"""
Конфигурация приложения LeetCode Practice CLI.

Содержит константы, пути и настройки.
"""

from pathlib import Path

# Пути
BASE_DIR = Path(__file__).parent
TASKS_DIR = BASE_DIR / "tasks"

# Настройки выполнения
EXECUTION_TIMEOUT = 5  # секунд на один тест
TOTAL_TIMEOUT = 30     # секунд на все тесты

# Язык по умолчанию
DEFAULT_LANGUAGE = "python3"

# Форматирование вывода
SEPARATOR = "─" * 40
DOUBLE_SEPARATOR = "═" * 40

# Цвета (ANSI escape codes)
class Colors:
    """ANSI escape codes для цветного вывода."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @classmethod
    def success(cls, text: str) -> str:
        """Зелёный текст для успешных операций."""
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def error(cls, text: str) -> str:
        """Красный текст для ошибок."""
        return f"{cls.RED}{text}{cls.RESET}"

    @classmethod
    def warning(cls, text: str) -> str:
        """Жёлтый текст для предупреждений."""
        return f"{cls.YELLOW}{text}{cls.RESET}"

    @classmethod
    def info(cls, text: str) -> str:
        """Голубой текст для информации."""
        return f"{cls.CYAN}{text}{cls.RESET}"

    @classmethod
    def muted(cls, text: str) -> str:
        """Серый текст для второстепенной информации."""
        return f"{cls.GRAY}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Жирный текст."""
        return f"{cls.BOLD}{text}{cls.RESET}"
