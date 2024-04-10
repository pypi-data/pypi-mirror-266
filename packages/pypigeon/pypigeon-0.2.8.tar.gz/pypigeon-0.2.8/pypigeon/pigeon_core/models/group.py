import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.group_role import GroupRole
from ..models.user_membership import UserMembership
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """Group model

    Attributes:
        created_on (datetime.datetime):
        group_name (str):
        subject_id (str):
        id (Union[Unset, str]):
        role (Union[Unset, GroupRole]):
        users (Union[Unset, List['UserMembership']]):
    """

    created_on: datetime.datetime
    group_name: str
    subject_id: str
    id: Union[Unset, str] = UNSET
    role: Union[Unset, GroupRole] = UNSET
    users: Union[Unset, List["UserMembership"]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        created_on = self.created_on.isoformat()
        group_name = self.group_name
        subject_id = self.subject_id
        id = self.id
        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        users: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.users, Unset):
            users = []
            for users_item_data in self.users:
                users_item = users_item_data.to_dict()
                users.append(users_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "created_on": created_on,
                "group_name": group_name,
                "subject_id": subject_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if role is not UNSET:
            field_dict["role"] = role
        if users is not UNSET:
            field_dict["users"] = users

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Group` from a dict"""
        d = src_dict.copy()
        created_on = isoparse(d.pop("created_on"))

        group_name = d.pop("group_name")

        subject_id = d.pop("subject_id")

        id = d.pop("id", UNSET)

        _role = d.pop("role", UNSET)
        role: Union[Unset, GroupRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = GroupRole(_role)

        users = []
        _users = d.pop("users", UNSET)
        for users_item_data in _users or []:
            users_item = UserMembership.from_dict(users_item_data)

            users.append(users_item)

        group = cls(
            created_on=created_on,
            group_name=group_name,
            subject_id=subject_id,
            id=id,
            role=role,
            users=users,
        )

        return group
