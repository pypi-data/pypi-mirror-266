from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.portfolio_transfer_view_request import PortfolioTransferViewRequest
from ...models.problem_details import ProblemDetails
from ...models.soa_account_list_api_result import SoaAccountListApiResult
from ...models.validation_problem_details import ValidationProblemDetails
from ...types import Response


def _get_kwargs(
    *,
    body: PortfolioTransferViewRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/api/v1-q2/Portfolio/view/transfers",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SoaAccountListApiResult.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ValidationProblemDetails.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ProblemDetails.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PortfolioTransferViewRequest,
) -> Response[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]:
    """Get Accounts Information for the portfolio.

    Args:
        body (PortfolioTransferViewRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PortfolioTransferViewRequest,
) -> Optional[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]:
    """Get Accounts Information for the portfolio.

    Args:
        body (PortfolioTransferViewRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PortfolioTransferViewRequest,
) -> Response[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]:
    """Get Accounts Information for the portfolio.

    Args:
        body (PortfolioTransferViewRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PortfolioTransferViewRequest,
) -> Optional[Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]]:
    """Get Accounts Information for the portfolio.

    Args:
        body (PortfolioTransferViewRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProblemDetails, SoaAccountListApiResult, ValidationProblemDetails]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
