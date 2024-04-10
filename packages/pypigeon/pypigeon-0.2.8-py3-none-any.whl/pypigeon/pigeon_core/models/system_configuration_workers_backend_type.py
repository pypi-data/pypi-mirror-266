from enum import Enum


class SystemConfigurationWorkersBackendType(str, Enum):
    SQLITE = "sqlite"

    def __str__(self) -> str:
        return str(self.value)
