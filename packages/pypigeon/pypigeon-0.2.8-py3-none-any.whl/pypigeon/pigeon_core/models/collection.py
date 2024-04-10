import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.collection_metadata import CollectionMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Collection")


@_attrs_define
class Collection:
    """Core collection properties, with IDs

    Attributes:
        account_id (str): The account containing this collection
        created_on (datetime.datetime):
        description (str): The collection's full description
        id (str):
        name (str): The collection's short human-readable name
        version_ids (List[str]): All available versions of the collection
        metadata (Union[Unset, CollectionMetadata]): Arbitrary user-defined metadata, key-value pairs
    """

    account_id: str
    created_on: datetime.datetime
    description: str
    id: str
    name: str
    version_ids: List[str]
    metadata: Union[Unset, "CollectionMetadata"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        created_on = self.created_on.isoformat()
        description = self.description
        id = self.id
        name = self.name
        version_ids = self.version_ids

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account_id": account_id,
                "createdOn": created_on,
                "description": description,
                "id": id,
                "name": name,
                "versionIds": version_ids,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Collection` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id")

        created_on = isoparse(d.pop("createdOn"))

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        version_ids = cast(List[str], d.pop("versionIds"))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CollectionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CollectionMetadata.from_dict(_metadata)

        collection = cls(
            account_id=account_id,
            created_on=created_on,
            description=description,
            id=id,
            name=name,
            version_ids=version_ids,
            metadata=metadata,
        )

        return collection
