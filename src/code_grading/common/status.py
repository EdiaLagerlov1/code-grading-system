"""Status constants and enums."""

from enum import Enum


class Status(str, Enum):
    """Task status values."""

    PENDING = "pending"
    READY = "ready"
    ERROR = "error"
    COMPLETED = "completed"

    def __str__(self) -> str:
        return self.value
