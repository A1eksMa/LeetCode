"""Domain enumerations for PracticeRaptor v1.6."""

from enum import Enum


class Language(str, Enum):
    """Supported interface languages (i18n)."""

    EN = "en"
    RU = "ru"


class ProgrammingLanguage(str, Enum):
    """Supported programming languages for code execution."""

    PYTHON = "python3"
    JAVA = "java"


class TextEditor(str, Enum):
    """Supported text editors for CLI."""

    DEFAULT = "default"
    NANO = "nano"
    VIM = "vim"


class Difficulty(str, Enum):
    """Problem difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(str, Enum):
    """Problem categories (algorithmic topics)."""

    ARRAY = "Array"
    STRING = "String"
    HASH_TABLE = "Hash Table"
    TWO_POINTERS = "Two Pointers"
    LINKED_LIST = "Linked List"
    STACK = "Stack"
    QUEUE = "Queue"
    TREE = "Tree"
    GRAPH = "Graph"
    BINARY_SEARCH = "Binary Search"
    DYNAMIC_PROGRAMMING = "Dynamic Programming"
    GREEDY = "Greedy"
    BACKTRACKING = "Backtracking"
    BIT_MANIPULATION = "Bit Manipulation"
    MATH = "Math"
    SORTING = "Sorting"
    HEAP = "Heap"


class Complexity(str, Enum):
    """Algorithmic complexity (Big O notation)."""

    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N2 = "O(n²)"
    O_N3 = "O(n³)"
    O_2N = "O(2ⁿ)"
    O_N_FACTORIAL = "O(n!)"


class ProblemStatus(str, Enum):
    """User progress status on a problem."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"


class ExecutionStatus(str, Enum):
    """Status of code execution result."""

    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    SYNTAX_ERROR = "syntax_error"
