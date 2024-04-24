"""REST client handling, including PncpStream base class."""
import logging

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk.helpers.jsonpath import extract_jsonpath  # type: ignore
from singer_sdk.streams import RESTStream  # type: ignore
from time import sleep

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class PncpStream(RESTStream):
    """Pncp stream class."""
    name = "PncpStream"
    __max_retries = 4

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        logging.info(self.config["url_base"])
        return self.config["url_base"]

    records_jsonpath = None

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")

        return headers

    def get_url_params(
            self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""

        params: dict = {}

        if next_page_token:
            params["pagina"] = next_page_token
        else:
            params["pagina"] = self.config.get("first_page")

        return params

    def backoff_max_tries(self) -> int:
        return self.__max_retries

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""

        if response.status_code == 204:
            return None
        elif response.status_code == 503:
            sleep(30)
            raise (RuntimeError(self.name, self.context))
        elif response.status_code >= 300:
            raise (RuntimeError(self.name, self.context))

        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """Add 'sub' uasg and agency fields if they exist and are None / null"""

        if ("orgaoSubRogado" in row) and (row["orgaoSubRogado"] is None):
            row["orgaoSubRogado"] = {
                "cnpj": None,
                "razaoSocial": None,
                "esferaId": None,
                "poderId": None
            }

        if ("unidadeSubRogada" in row) and (row["unidadeSubRogada"] is None):
            row["unidadeSubRogada"] = {
                "ufNome": None,
                "codigoUnidade": None,
                "nomeUnidade": None,
                "ufSigla": None,
                "municipioNome": None,
                "codigoIbge": None
            }

        return row
