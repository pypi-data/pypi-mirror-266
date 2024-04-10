"""List collections"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_get_collections_collection_list import (
    CollectionsGetCollectionsCollectionList,
)
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
    not_account_id: Union[Unset, str] = UNSET,
    public: Union[Unset, bool] = UNSET,
    starred: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["name"] = name

    params["account_id"] = account_id

    params["not_account_id"] = not_account_id

    params["public"] = public

    params["starred"] = starred

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionsGetCollectionsCollectionList, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionsGetCollectionsCollectionList.from_dict(
            response.json()
        )

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CollectionsGetCollectionsCollectionList, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
    not_account_id: Union[Unset, str] = UNSET,
    public: Union[Unset, bool] = UNSET,
    starred: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Response[Union[CollectionsGetCollectionsCollectionList, ServerError]]:
    """List collections

    List all collections that are visible to the current user,
    whether logged in or not.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):
        not_account_id (Union[Unset, str]):
        public (Union[Unset, bool]):
        starred (Union[Unset, bool]):
        page_size (Union[Unset, int]):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsGetCollectionsCollectionList, ServerError]]
    """

    kwargs = _get_kwargs(
        name=name,
        account_id=account_id,
        not_account_id=not_account_id,
        public=public,
        starred=starred,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
    not_account_id: Union[Unset, str] = UNSET,
    public: Union[Unset, bool] = UNSET,
    starred: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Union[CollectionsGetCollectionsCollectionList]:
    """List collections

    List all collections that are visible to the current user,
    whether logged in or not.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):
        not_account_id (Union[Unset, str]):
        public (Union[Unset, bool]):
        starred (Union[Unset, bool]):
        page_size (Union[Unset, int]):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsGetCollectionsCollectionList]
    """

    response = sync_detailed(
        client=client,
        name=name,
        account_id=account_id,
        not_account_id=not_account_id,
        public=public,
        starred=starred,
        page_size=page_size,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
    not_account_id: Union[Unset, str] = UNSET,
    public: Union[Unset, bool] = UNSET,
    starred: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Response[Union[CollectionsGetCollectionsCollectionList, ServerError]]:
    """List collections

    List all collections that are visible to the current user,
    whether logged in or not.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):
        not_account_id (Union[Unset, str]):
        public (Union[Unset, bool]):
        starred (Union[Unset, bool]):
        page_size (Union[Unset, int]):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsGetCollectionsCollectionList, ServerError]]
    """

    kwargs = _get_kwargs(
        name=name,
        account_id=account_id,
        not_account_id=not_account_id,
        public=public,
        starred=starred,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
    not_account_id: Union[Unset, str] = UNSET,
    public: Union[Unset, bool] = UNSET,
    starred: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Union[CollectionsGetCollectionsCollectionList]:
    """List collections

    List all collections that are visible to the current user,
    whether logged in or not.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):
        not_account_id (Union[Unset, str]):
        public (Union[Unset, bool]):
        starred (Union[Unset, bool]):
        page_size (Union[Unset, int]):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsGetCollectionsCollectionList]
    """

    response = await asyncio_detailed(
        client=client,
        name=name,
        account_id=account_id,
        not_account_id=not_account_id,
        public=public,
        starred=starred,
        page_size=page_size,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
