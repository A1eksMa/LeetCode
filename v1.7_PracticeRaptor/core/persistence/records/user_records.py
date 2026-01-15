"""User persistence records.

Each record corresponds to a JSON file or SQL table.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass


@dataclass
class UserRecord:
    """User entity with authentication data.

    Maps to: users.json / TABLE users
    Primary key: user_id
    """

    user_id: int = 0
    user_name: str = "guest"
    hash_password: str = ""
