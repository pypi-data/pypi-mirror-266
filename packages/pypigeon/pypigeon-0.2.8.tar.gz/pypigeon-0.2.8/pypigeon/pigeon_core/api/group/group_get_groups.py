"""List groups"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.group_get_groups_response_200 import GroupGetGroupsResponse200
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    users: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["users"] = users

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/group",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[GroupGetGroupsResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GroupGetGroupsResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GroupGetGroupsResponse200, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    users: Union[Unset, bool] = UNSET,
) -> Response[Union[GroupGetGroupsResponse200, ServerError]]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GroupGetGroupsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        users=users,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    users: Union[Unset, bool] = UNSET,
) -> Union[GroupGetGroupsResponse200]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GroupGetGroupsResponse200]
    """

    response = sync_detailed(
        client=client,
        users=users,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    users: Union[Unset, bool] = UNSET,
) -> Response[Union[GroupGetGroupsResponse200, ServerError]]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GroupGetGroupsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        users=users,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    users: Union[Unset, bool] = UNSET,
) -> Union[GroupGetGroupsResponse200]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GroupGetGroupsResponse200]
    """

    response = await asyncio_detailed(
        client=client,
        users=users,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
