import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse


T = TypeVar("T", bound="Account")


@_attrs_define
class Account:
    """Account model

    Attributes:
        account_id (str):
        created_on (datetime.datetime):
        is_personal (bool):
        name (str):
    """

    account_id: str
    created_on: datetime.datetime
    is_personal: bool
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        created_on = self.created_on.isoformat()
        is_personal = self.is_personal
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account_id": account_id,
                "created_on": created_on,
                "is_personal": is_personal,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Account` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id")

        created_on = isoparse(d.pop("created_on"))

        is_personal = d.pop("is_personal")

        name = d.pop("name")

        account = cls(
            account_id=account_id,
            created_on=created_on,
            is_personal=is_personal,
            name=name,
        )

        return account
