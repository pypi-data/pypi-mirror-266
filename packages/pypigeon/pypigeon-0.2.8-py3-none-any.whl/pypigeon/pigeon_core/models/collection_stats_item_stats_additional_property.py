from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="CollectionStatsItemStatsAdditionalProperty")


@_attrs_define
class CollectionStatsItemStatsAdditionalProperty:
    """CollectionStatsItemStatsAdditionalProperty model

    Attributes:
        num_items (int):
        size_bytes (int):
    """

    num_items: int
    size_bytes: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        num_items = self.num_items
        size_bytes = self.size_bytes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "numItems": num_items,
                "sizeBytes": size_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionStatsItemStatsAdditionalProperty` from a dict"""
        d = src_dict.copy()
        num_items = d.pop("numItems")

        size_bytes = d.pop("sizeBytes")

        collection_stats_item_stats_additional_property = cls(
            num_items=num_items,
            size_bytes=size_bytes,
        )

        return collection_stats_item_stats_additional_property
