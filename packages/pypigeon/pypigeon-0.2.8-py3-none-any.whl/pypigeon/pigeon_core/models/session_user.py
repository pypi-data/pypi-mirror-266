from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.identity import Identity
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SessionUser")


@_attrs_define
class SessionUser:
    """SessionUser model

    Attributes:
        identity (Identity):
        name (str):
        account_id (Union[Unset, str]):
        email (Union[Unset, str]):
        image (Union[Unset, str]):
    """

    identity: "Identity"
    name: str
    account_id: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    image: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        identity = self.identity.to_dict()
        name = self.name
        account_id = self.account_id
        email = self.email
        image = self.image

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identity": identity,
                "name": name,
            }
        )
        if account_id is not UNSET:
            field_dict["account_id"] = account_id
        if email is not UNSET:
            field_dict["email"] = email
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SessionUser` from a dict"""
        d = src_dict.copy()
        identity = Identity.from_dict(d.pop("identity"))

        name = d.pop("name")

        account_id = d.pop("account_id", UNSET)

        email = d.pop("email", UNSET)

        image = d.pop("image", UNSET)

        session_user = cls(
            identity=identity,
            name=name,
            account_id=account_id,
            email=email,
            image=image,
        )

        return session_user
