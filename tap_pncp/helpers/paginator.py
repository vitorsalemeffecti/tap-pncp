from typing import Optional
from requests import Response
from singer_sdk.pagination import BaseAPIPaginator  # type: ignore

from . import TPageToken


class PncpBasePaginator(BaseAPIPaginator):
    """Get next page value or None if there are no more pages. It works for cases when the response contains numeroPagina and paginasRestantes"""

    def get_next(self, response: Response) -> Optional[TPageToken]:

        if response is None:
            return None

        if 'numeroPagina' in response.json():
            actual_page_number = response.json()['numeroPagina']
            remaining_pages = response.json()['paginasRestantes']

            if remaining_pages and (remaining_pages > 0):
                return actual_page_number + 1

        return None
