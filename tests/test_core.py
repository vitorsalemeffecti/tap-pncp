"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class # type: ignore

from tap_pncp.tap import TapPncp


SAMPLE_CONFIG = {
    "initial_date": "20230909",
    "final_date": "20230909",
    "first_page": 1,
    "url_base": "https://pncp.gov.br/api"    
}


# Run standard built-in tap tests from the SDK:
TestTapPncp = get_tap_test_class(
    tap_class=TapPncp,
    config=SAMPLE_CONFIG,
)

TestTapPncp