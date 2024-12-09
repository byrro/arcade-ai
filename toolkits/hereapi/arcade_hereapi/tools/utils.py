from urllib.parse import urlencode

from arcade_hereapi.tools.constants import HERE_API_BASE_URL

from arcade.core.user_agent import USER_AGENT


def get_url(*, endpoint: str, **query_args: dict[str, str]) -> str:
    """
    Get the full URL for a given endpoint.

    :param endpoint: The endpoint key from ENDPOINTS
    :param query_args: The query arguments for the URL
    :return: The full URL
    """
    return f"{HERE_API_BASE_URL}/{endpoint}?{urlencode(query_args)}"


def get_headers() -> dict[str, str]:
    return {
        "Accept-Encoding": "gzip",
        # DISCUSS:
        # Is it ok to add the ArcadeAI user-agent?
        "User-Agent": USER_AGENT,
    }
