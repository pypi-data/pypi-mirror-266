import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.group import Group
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """User model

    Attributes:
        account_id (str):
        created_on (datetime.datetime):
        subject_id (str):
        user_name (str):
        given_name (Union[Unset, str]):
        groups (Union[Unset, List['Group']]): Names and ids of the groups this user belongs to
        id (Union[Unset, str]):
        last_name (Union[Unset, str]):
        user_email (Union[Unset, str]):
    """

    account_id: str
    created_on: datetime.datetime
    subject_id: str
    user_name: str
    given_name: Union[Unset, str] = UNSET
    groups: Union[Unset, List["Group"]] = UNSET
    id: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    user_email: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        created_on = self.created_on.isoformat()
        subject_id = self.subject_id
        user_name = self.user_name
        given_name = self.given_name
        groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)

        id = self.id
        last_name = self.last_name
        user_email = self.user_email

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account_id": account_id,
                "created_on": created_on,
                "subject_id": subject_id,
                "user_name": user_name,
            }
        )
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if groups is not UNSET:
            field_dict["groups"] = groups
        if id is not UNSET:
            field_dict["id"] = id
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if user_email is not UNSET:
            field_dict["user_email"] = user_email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`User` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id")

        created_on = isoparse(d.pop("created_on"))

        subject_id = d.pop("subject_id")

        user_name = d.pop("user_name")

        given_name = d.pop("given_name", UNSET)

        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in _groups or []:
            groups_item = Group.from_dict(groups_item_data)

            groups.append(groups_item)

        id = d.pop("id", UNSET)

        last_name = d.pop("last_name", UNSET)

        user_email = d.pop("user_email", UNSET)

        user = cls(
            account_id=account_id,
            created_on=created_on,
            subject_id=subject_id,
            user_name=user_name,
            given_name=given_name,
            groups=groups,
            id=id,
            last_name=last_name,
            user_email=user_email,
        )

        return user
