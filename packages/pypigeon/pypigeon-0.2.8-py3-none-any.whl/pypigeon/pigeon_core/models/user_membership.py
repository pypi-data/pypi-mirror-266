from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.group_role import GroupRole


T = TypeVar("T", bound="UserMembership")


@_attrs_define
class UserMembership:
    """UserMembership model

    Attributes:
        id (str):
        role (GroupRole):
    """

    id: str
    role: GroupRole

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        id = self.id
        role = self.role.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UserMembership` from a dict"""
        d = src_dict.copy()
        id = d.pop("id")

        role = GroupRole(d.pop("role"))

        user_membership = cls(
            id=id,
            role=role,
        )

        return user_membership
