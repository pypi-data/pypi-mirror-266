from pypigeon.pigeon_core.api.admin import admin_grant_admin
from pypigeon.pigeon_core.api.admin import admin_list_admins
from pypigeon.pigeon_core.api.user import user_get_users
from pypigeon.pigeon_core.models import AdminGrantAdminAdminListRequest
from pypigeon.pigeon_core.models import AdminGrants
from pypigeon.pigeon_core.models import UserGetUsersResponse200
from pypigeon.pigeon_core.paginator import Paginator

from .base_commands import BaseCommands


class UsersCommands(BaseCommands):
    """Operations on users"""

    def list(self) -> None:
        """List users."""
        pager = Paginator[UserGetUsersResponse200](user_get_users, self.core)

        data = []
        for page in pager.paginate():
            data.extend([u.to_dict() for u in page.users])

        self._output(data, preferred_type="table")

    def admins_list(self) -> None:
        """Retrieve the current list of admins."""
        admins = admin_list_admins.sync(client=self.core)

        self._output([g.to_dict() for g in admins.grants], preferred_type="table")

    @BaseCommands._with_arg("subject_id")
    @BaseCommands._with_arg("-o", "--operation")
    def admins_add(self) -> None:
        """Add an admin."""
        admins = admin_list_admins.sync(client=self.core)

        if self.args.operation:
            new_operations = {self.args.operation}
        else:
            new_operations = set(admins.operations or [])

        for grant in admins.grants:
            if grant.subject_id == self.args.subject_id:
                grant.operations = list(set(grant.operations) | new_operations)
                break
        else:
            admins.grants.append(
                AdminGrants(
                    subject_id=self.args.subject_id, operations=list(new_operations)
                )
            )

        admin_grant_admin.sync(
            body=AdminGrantAdminAdminListRequest(grants=admins.grants), client=self.core
        )

    @BaseCommands._with_arg("subject_id")
    def admins_revoke(self) -> None:
        """Revoke all admin privileges from a user."""
        admins = admin_list_admins.sync(client=self.core)

        new_grants = [g for g in admins.grants if g.subject_id != self.args.subject_id]
        if new_grants == admins.grants:
            raise ValueError(f"{self.args.subject_id} is not listed in admins")

        admin_grant_admin.sync(
            body=AdminGrantAdminAdminListRequest(grants=new_grants), client=self.core
        )
