from enum import Enum


class ItemStatusDetailStatus(str, Enum):
    FAILED = "failed"
    NOT_APPLICABLE = "not-applicable"
    OK = "ok"
    PENDING = "pending"
    SERVER_ERROR = "server-error"

    def __str__(self) -> str:
        return str(self.value)
