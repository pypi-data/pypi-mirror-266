from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="OauthProvider")


@_attrs_define
class OauthProvider:
    """OauthProvider model

    Attributes:
        callback_url (str):
        id (str):
        name (str):
        signin_url (str):
        type (str):
    """

    callback_url: str
    id: str
    name: str
    signin_url: str
    type: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        callback_url = self.callback_url
        id = self.id
        name = self.name
        signin_url = self.signin_url
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "callbackUrl": callback_url,
                "id": id,
                "name": name,
                "signinUrl": signin_url,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`OauthProvider` from a dict"""
        d = src_dict.copy()
        callback_url = d.pop("callbackUrl")

        id = d.pop("id")

        name = d.pop("name")

        signin_url = d.pop("signinUrl")

        type = d.pop("type")

        oauth_provider = cls(
            callback_url=callback_url,
            id=id,
            name=name,
            signin_url=signin_url,
            type=type,
        )

        return oauth_provider
