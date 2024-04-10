from datetime import datetime

from pypigeon.client import PigeonClient


def test_get_collection_by_name(httpx_mock, client):
    httpx_mock.add_response(
        url="https://pigeon.test/api/v1/collections?name=test&page_size=50",
        json={
            "collections": [
                {
                    "id": "xyz",
                    "account_id": "aaa",
                    "createdOn": datetime.now().isoformat(),
                    "description": "",
                    "name": "XYZ",
                    "versionIds": ["LIVE"],
                    "metadata": {},
                }
            ],
            "pagination": {
                "total_items": 1,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    p = PigeonClient(client)
    collection = p.get_collection_by_name("test")
    assert collection.id == "xyz"
