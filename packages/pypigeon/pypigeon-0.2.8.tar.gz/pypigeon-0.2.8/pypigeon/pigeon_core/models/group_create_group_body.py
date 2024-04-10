from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="GroupCreateGroupBody")


@_attrs_define
class GroupCreateGroupBody:
    """GroupCreateGroupBody model

    Attributes:
        group_name (str):
    """

    group_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        group_name = self.group_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "group_name": group_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`GroupCreateGroupBody` from a dict"""
        d = src_dict.copy()
        group_name = d.pop("group_name")

        group_create_group_body = cls(
            group_name=group_name,
        )

        return group_create_group_body
