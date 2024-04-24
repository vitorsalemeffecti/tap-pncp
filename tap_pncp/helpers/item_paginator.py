from typing import Optional
from requests import Response
from singer_sdk.pagination import BaseAPIPaginator  # type:ignore

from . import TPageToken


class ItemsPaginator(BaseAPIPaginator):
    """Returns a token for identifying next page or None if no more pages."""

    page_size_limit = None

    def get_next(self, response: Response) -> Optional[TPageToken]:
        if response is None:
            return None

        if isinstance(response.json(), list) and (len(response.json()) == self.page_size_limit):
            return self._value + 1

        return None

    def set_page_size_limit(self, page_size: int):
        self.page_size_limit = page_size
