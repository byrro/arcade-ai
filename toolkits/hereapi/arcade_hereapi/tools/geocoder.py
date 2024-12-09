from typing import Annotated, Optional

import httpx
from arcade_hereapi.tools.utils import get_headers, get_url

from arcade.sdk import ToolContext, tool
from arcade.sdk.errors import ToolExecutionError


@tool
async def geocode_address(
    context: ToolContext,
    address: Annotated[str, "The address string to search for geocoded results"],
    limit: Annotated[Optional[int], "The maximum number of items to return"] = None,
) -> Annotated[list[dict], "A list of geocoded address results"]:
    """
    Geocode an address string into a structured format with precise geo-coordinates
    """
    query_args = {
        "q": address,
        "types": "address",
        "apiKey": context.authorization.token,
    }

    if limit:
        query_args["limit"] = limit

    url = get_url(endpoint="geocode", **query_args)
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["items"]
        except httpx.RequestError as e:
            raise ToolExecutionError(f"Failed to send request to HERE API: {e}") from e
