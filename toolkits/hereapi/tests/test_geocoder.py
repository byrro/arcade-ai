import copy
from unittest.mock import AsyncMock, patch

import pytest
from arcade_hereapi.tools.constants import DEFAULT_MIN_QUERY_SCORE
from arcade_hereapi.tools.geocoder import get_structured_address
from arcade_hereapi.tools.utils import get_headers, get_url
from httpx import Request, Response

from arcade.sdk.errors import ToolExecutionError

MOCK_RESPONSE = {
    "items": [
        {
            "title": "Lombard St, San Francisco, CA 94109, United States",
            "id": "here:af:streetsection:txsQzQBaGGhhFYGezc2Z8B",
            "resultType": "street",
            "address": {
                "label": "Lombard St, San Francisco, CA 94109, United States",
                "countryCode": "USA",
                "countryName": "United States",
                "stateCode": "CA",
                "state": "California",
                "county": "San Francisco",
                "city": "San Francisco",
                "district": "Russian Hill",
                "street": "Lombard St",
                "postalCode": "94109",
            },
            "position": {"lat": 37.80178, "lng": -122.42124},
            "mapView": {
                "west": -122.42449,
                "south": 37.80133,
                "east": -122.41798,
                "north": 37.80223,
            },
            "scoring": {"queryScore": 1.0, "fieldScore": {"streets": [1.0]}},
        }
    ]
}


@pytest.fixture
def mock_token():
    return "mock_token"


@pytest.fixture
def mock_context(mock_token: str):
    context = AsyncMock()
    context.authorization.token = mock_token
    return context


@pytest.fixture
def mock_client():
    with patch("arcade_hereapi.tools.geocoder.httpx.AsyncClient") as client:
        yield client.return_value.__aenter__.return_value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "address,here_response,tool_response,min_query_score",
    [
        ("unknown street", {"items": []}, None, 0.85),
        (
            "lombard street",
            MOCK_RESPONSE,
            {
                **MOCK_RESPONSE["items"][0]["address"],
                "position": {
                    "latitude": MOCK_RESPONSE["items"][0]["position"]["lat"],
                    "longitude": MOCK_RESPONSE["items"][0]["position"]["lng"],
                },
            },
            0.85,
        ),
    ],
)
async def test_get_structured_address_success(
    mock_context,
    mock_client,
    mock_token,
    address,
    here_response,
    tool_response,
    min_query_score,
):
    url = get_url(endpoint="geocode", q=address, types="address", apiKey=mock_token)
    request = Request(method="GET", url=url, headers=get_headers())
    mock_client.get.return_value = Response(
        status_code=200,
        json=here_response,
        request=request,
    )

    result = await get_structured_address(
        context=mock_context,
        address=address,
        min_query_score=min_query_score,
    )
    assert result == tool_response


@pytest.mark.asyncio
async def test_get_structured_address_low_query_score(mock_context, mock_client, mock_token):
    url = get_url(endpoint="geocode", q="geocode", types="address", apiKey=mock_token)
    request = Request(method="GET", url=url, headers=get_headers())
    here_response = copy.deepcopy(MOCK_RESPONSE)
    here_response["items"][0]["scoring"]["queryScore"] = DEFAULT_MIN_QUERY_SCORE - 0.1
    mock_client.get.return_value = Response(
        status_code=200,
        json=here_response,
        request=request,
    )

    result = await get_structured_address(context=mock_context, address="ambiguous street")
    assert result is None


@pytest.mark.asyncio
async def test_get_structured_address_rate_limit_exceeded(mock_context, mock_client, mock_token):
    url = get_url(endpoint="geocode", q="geocode", types="address", apiKey=mock_token)
    request = Request(method="GET", url=url, headers=get_headers())
    mock_client.get.return_value = Response(
        status_code=429,
        json={"status": 429, "title": "Rate limit exceeded"},
        request=request,
    )

    with pytest.raises(ToolExecutionError):
        await get_structured_address(context=mock_context, address="too many streets")
