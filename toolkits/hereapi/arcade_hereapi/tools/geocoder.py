from typing import Annotated, Optional

import httpx
from arcade_hereapi.tools.constants import DEFAULT_MIN_QUERY_SCORE
from arcade_hereapi.tools.utils import get_headers, get_url

from arcade.sdk import ToolContext, tool
from arcade.sdk.auth import Here as HereAuth
from arcade.sdk.errors import ToolExecutionError


# Implements https://www.here.com/docs/bundle/geocoding-and-search-api-v7-api-reference/page/index.html
# Example arcade chat usage: "get the structured address data for <ADDRESS>"
# DISCUSS:
# I implemented a simple ApiKeyAuth class in the core sdk to use here as authorization
@tool(requires_auth=HereAuth())
async def get_structured_address(
    context: ToolContext,
    address: Annotated[str, "The address string to get structured data about"],
    # DISCUSS:
    # Is it a good idea to expose such argument to the LLM? Perhaps it could get
    # tempted into setting a very low value just to get a response and fulfill the
    # user request, but with a potentially wrong match...
    min_query_score: Annotated[
        float, "The minimum query score (from 0 to 1) to consider an address a valid match"
    ] = DEFAULT_MIN_QUERY_SCORE,
) -> Annotated[
    Optional[dict],
    (
        # DISCUSS:
        # There's got to be a better way to hint the LLM about the expected response...
        "A dictionary containing structured address data with the keys: countryCode, "
        "countryName, stateCode, state, county, city, district, street, postalCode, "
        "houseNumber, and position (latitude, longitude coordinates). "
        "Returns None if the address is not found."
    ),
]:
    """
    Geocode an unstructured address string into a structured dictionary
    """
    query_args = {
        "q": address,
        "types": "address",
        "limit": 1,
        "apiKey": context.authorization.token,
    }

    url = get_url(endpoint="geocode", **query_args)
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            items = response.json()["items"]

            if not items:
                return None

            if items[0]["scoring"]["queryScore"] < min_query_score:
                return None

            # DISCUSS:
            # Would it be better to let an exception be raised if the address or
            # position keys aren't present in the HERE API response?
            return {
                **items[0].get("address", {}),
                "position": {
                    "latitude": items[0].get("position", {}).get("lat"),
                    "longitude": items[0].get("position", {}).get("lng"),
                },
            }

        except httpx.RequestError as e:
            # DISCUSS:
            # Other tools don't raise `ToolExecutionError` using `from e`.
            # Should we follow this as a pattern?
            raise ToolExecutionError(
                f"Failed to get structured address data from HERE API: {e}"
            ) from e
