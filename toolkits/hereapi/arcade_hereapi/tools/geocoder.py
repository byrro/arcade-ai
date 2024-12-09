from typing import Annotated, Optional

import httpx
from arcade_hereapi.tools.utils import get_headers, get_url

from arcade.sdk import ToolContext, tool
from arcade.sdk.auth import Here as HereAuth
from arcade.sdk.errors import ToolExecutionError


# Implements https://www.here.com/docs/bundle/geocoding-and-search-api-v7-api-reference/page/index.html
# Example arcade chat usage: "get the structured address data for <ADDRESS>"
@tool(requires_auth=HereAuth())
async def get_structured_address(
    context: ToolContext,
    address: Annotated[str, "The address string to get structured data about"],
) -> Annotated[
    Optional[dict],
    (
        # DISCUSS:
        # There's got to be a better way to hint the LLM about the expected response...
        "A dictionary containing structured address data with the keys: countryCode, "
        "countryName, stateCode, state, county, city, district, street, postalCode, "
        "and latitude / longitude coordinates. "
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

            # DISCUSS:
            # Would it be better to let an exception be raise if the address or position
            # keys aren't present in the HERE API response?
            return {
                **items[0].get("address", {}),
                "position": items[0].get("position"),
            }

        except httpx.RequestError as e:
            # DISCUSS:
            # Other tools don't raise `ToolExecutionError` using `from e`.
            # Should we follow this as a pattern?
            raise ToolExecutionError(
                f"Failed to get structured address data from HERE API: {e}"
            ) from e
