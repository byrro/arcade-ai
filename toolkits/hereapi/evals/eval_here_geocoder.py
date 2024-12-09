import arcade_hereapi
from arcade_hereapi.tools.constants import DEFAULT_MIN_QUERY_SCORE
from arcade_hereapi.tools.geocoder import get_structured_address

from arcade.sdk import ToolCatalog
from arcade.sdk.eval import (
    BinaryCritic,
    EvalRubric,
    EvalSuite,
    SimilarityCritic,
    tool_eval,
)

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.9,
    warn_threshold=0.95,
)

catalog = ToolCatalog()
catalog.add_module(arcade_hereapi)


@tool_eval()
def calendar_eval_suite() -> EvalSuite:
    """Create an evaluation suite for HERE API tools."""
    suite = EvalSuite(
        name="HERE API Tools Evaluation",
        system_message=(
            "You are an AI assistant that can geocode an unstructured address string "
            "into a structured and standardized dictionary format."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    suite.add_case(
        name="Get structured address data",
        user_message=(
            "Get the following address in a structured format: '1600 Amphitheatre "
            "Parkway, Mountain View, CA'"
        ),
        expected_tool_calls=[
            (
                get_structured_address,
                {
                    "address": "1600 Amphitheatre Parkway, Mountain View, CA",
                    "min_query_score": DEFAULT_MIN_QUERY_SCORE,
                },
            )
        ],
        critics=[
            BinaryCritic(
                critic_field="countryCode",
                expected="USA",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="countryName",
                expected="United States",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="stateCode",
                expected="CA",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="state",
                expected="California",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="county",
                expected="Santa Clara",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="city",
                expected="Mountain View",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="street",
                expected="Amphitheatre Parkway",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="postalCode",
                expected="94043-1351",
                weight=0.1,
            ),
            BinaryCritic(
                critic_field="houseNumber",
                expected="1600",
                weight=0.2,
            ),
            SimilarityCritic(
                critic_field="position",
                expected=str({"lat": 37.42249, "lng": -122.08473}),
                weight=0.2,
            ),
        ],
    )

    suite.add_case(
        name="Get latitude and longitude for an address",
        user_message=(
            "Get the the latitude and longitude coordinates for the address: "
            "'1600 Amphitheatre Parkway, Mountain View, CA'"
        ),
        expected_tool_calls=[
            (
                get_structured_address,
                {
                    "address": "1600 Amphitheatre Parkway, Mountain View, CA",
                    "min_query_score": DEFAULT_MIN_QUERY_SCORE,
                },
            )
        ],
        critics=[
            SimilarityCritic(
                critic_field="position",
                expected=str({"lat": 37.42249, "lng": -122.08473}),
                weight=1,
            ),
        ],
    )
