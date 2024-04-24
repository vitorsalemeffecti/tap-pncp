"""pncp tap class."""

from typing import List

from singer_sdk import Tap, Stream  # type: ignore
from singer_sdk import typing as th  # type: ignore

from tap_pncp.streams import (
    ContractsStream,
    PurchasesStream,
    ItemsStream,
    ItemResultsStream,
)

STREAM_TYPES = [
    ContractsStream,
    PurchasesStream,
    ItemsStream,
    ItemResultsStream,
]


class TapPncp(Tap):
    """pncp tap class."""
    name = "tap-pncp"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "project_id",
            th.StringType,
            required=False,
            description="Project ID to replicate"
        ),
        th.Property(
            "initial_date",
            th.StringType,
            required=True,
            description="The earliest record date to sync"
        ),
        th.Property(
            "final_date",
            th.StringType,
            required=True,
            description="The earliest record date to sync"
        ),
        th.Property(
            "first_page",
            th.IntegerType,
            required=True,
            description="Starting page number"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


#  need for debugging https://docs.meltano.com/guide/debugging-custom-extractor/#add-a-main-block-in-tappy-of-your-custom-extractor
if __name__ == "__main__":
    TapPncp.cli()
