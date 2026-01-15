"""Domain enumerations."""

from enum import Enum


class Language(str, Enum):
    """Supported languages for UI."""

    EN = "en"
    RU = "ru"


class ProgrammingLanguage(str, Enum):
    """Programming language for code execution."""

    PYTHON = "python3"
    JAVA = "java"


class TextEditor(str, Enum):
    """Preferred text editor for code editing."""

    DEFAULT = "default"
    NANO = "nano"
    VIM = "vim"


class Difficulty(str, Enum):
    """Problem difficulty level."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(str, Enum):
    """Algorithmic problem category."""

    ARRAY = "Array"
    STRING = "String"
    HASH_TABLE = "Hash Table"
    LINKED_LIST = "Linked List"
    STACK = "Stack"
    QUEUE = "Queue"
    TREE = "Tree"
    GRAPH = "Graph"
    SORTING = "Sorting"
    BINARY_SEARCH = "Binary Search"
    DYNAMIC_PROGRAMMING = "Dynamic Programming"
    GREEDY = "Greedy"
    BACKTRACKING = "Backtracking"
    RECURSION = "Recursion"
    MATH = "Math"
    BIT_MANIPULATION = "Bit Manipulation"
    TWO_POINTERS = "Two Pointers"


class Complexity(str, Enum):
    """Algorithmic complexity (Big O notation)."""

    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N_SQUARED = "O(n²)"
    O_N_CUBED = "O(n³)"
    O_2_N = "O(2ⁿ)"
    O_N_FACTORIAL = "O(n!)"


class ProblemStatus(str, Enum):
    """User's progress status on a problem."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"


class ExecutionStatus(str, Enum):
    """Code execution result status."""

    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    SYNTAX_ERROR = "syntax_error"
