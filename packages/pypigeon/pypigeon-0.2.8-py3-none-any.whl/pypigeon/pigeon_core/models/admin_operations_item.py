from enum import Enum


class AdminOperationsItem(str, Enum):
    ADMIN_CDE = "admin.cde"
    ADMIN_CONFIG = "admin.config"
    ADMIN_GRANTADMIN = "admin.grantadmin"
    ADMIN_METADATA = "admin.metadata"
    ADMIN_USERS = "admin.users"

    def __str__(self) -> str:
        return str(self.value)
