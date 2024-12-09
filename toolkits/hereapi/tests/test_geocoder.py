from unittest.mock import AsyncMock, patch

import pytest
from arcade_hereapi.tools.geocoder import get_structured_address
from arcade_hereapi.tools.utils import get_headers, get_url
from httpx import Request, Response

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
    "address,here_response,tool_response",
    [
        ("unknown street", {"items": []}, None),
        (
            "lombard street",
            MOCK_RESPONSE,
            {
                **MOCK_RESPONSE["items"][0]["address"],
                "position": MOCK_RESPONSE["items"][0]["position"],
            },
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
):
    url = get_url(endpoint="geocode", q=address, types="address", apiKey=mock_token)
    request = Request(method="GET", url=url, headers=get_headers())
    mock_client.get.return_value = Response(
        status_code=200,
        json=here_response,
        request=request,
    )

    result = await get_structured_address(context=mock_context, address=address)
    assert result == tool_response
