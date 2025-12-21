"""ANSI color codes for terminal output."""


class Colors:
    """ANSI escape codes for colored output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @classmethod
    def success(cls, text: str) -> str:
        """Green text for success."""
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def error(cls, text: str) -> str:
        """Red text for errors."""
        return f"{cls.RED}{text}{cls.RESET}"

    @classmethod
    def warning(cls, text: str) -> str:
        """Yellow text for warnings."""
        return f"{cls.YELLOW}{text}{cls.RESET}"

    @classmethod
    def info(cls, text: str) -> str:
        """Cyan text for info."""
        return f"{cls.CYAN}{text}{cls.RESET}"

    @classmethod
    def muted(cls, text: str) -> str:
        """Gray text for secondary info."""
        return f"{cls.GRAY}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Bold text."""
        return f"{cls.BOLD}{text}{cls.RESET}"


# Separators
SEPARATOR = "-" * 40
DOUBLE_SEPARATOR = "=" * 40
