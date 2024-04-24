"""Stream type classes for tap-pncp."""
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, TypeVar

TPageToken = TypeVar("TPageToken")

import re

from singer_sdk import typing as th  # type: ignore

from tap_pncp.client import PncpStream
from .helpers import PncpBasePaginator, ItemsPaginator, ChildStreamControl

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ContractsStream(PncpStream):
    """Contracts stream."""
    name = "pncp_contracts"
    path = "/consulta/v1/contratos"
    primary_keys = ["numeroControlePNCP", ]
    replication_key = "dataAtualizacao"

    schema_filepath = SCHEMAS_DIR / "contract.json"

    records_jsonpath = "$.data[*]"

    child_stream_control = ChildStreamControl()

    def get_new_paginator(self):
        return PncpBasePaginator(1)

    def get_url_params(
            self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Overrides the super class params adding date keys."""
        params = super().get_url_params(context, next_page_token)
        params['dataInicial'] = self.config.get("initial_date")
        params['dataFinal'] = self.config.get("final_date")
        logging.info(f'DATA CAPTURA: {params["dataInicial"]}')
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""

        purchase_control_id = record["numeroControlePncpCompra"]

        if self.child_stream_control.should_not_create(purchase_control_id):
            return None
        else:
            self.child_stream_control.add_to_control(purchase_control_id)

        ids_context = extract_ids(purchase_control_id)
        ids_context["numeroControlePncpCompra"] = purchase_control_id
        return ids_context


class PurchasesStream(PncpStream):
    """Purchases stream."""
    name = "pncp_purchases"

    path = "/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}"
    primary_keys = ["numeroControlePNCP", ]
    replication_key = "dataAtualizacao"
    schema_filepath = SCHEMAS_DIR / "purchase.json"

    records_jsonpath = "[*]"

    parent_stream_type = ContractsStream
    ignore_parent_replication_key = True


class ItemsStream(PncpStream):
    """Items stream."""
    name = "pncp_items"

    path = "/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"
    primary_keys = ["numeroControlePncpCompra", "numeroItem", ]
    replication_key = "dataAtualizacao"  # TODO: discuss about using situacaoCompraItem in place of this date

    schema_filepath = SCHEMAS_DIR / "item.json"

    records_jsonpath = "[*]"

    parent_stream_type = ContractsStream
    ignore_parent_replication_key = True

    page_size_param = 10

    def get_url_params(
            self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Overrides the super class params adding a 'page size' key."""
        params = super().get_url_params(context, next_page_token)
        params["tamanhoPagina"] = self.page_size_param

        return params

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """Add numeroControlePncpCompra field to item"""

        row["numeroControlePncpCompra"] = context["numeroControlePncpCompra"]

        return row

    def get_new_paginator(self):
        """Overrides to handle the items page's records limit set in the attribute page_size_param"""
        itemsPaginator = ItemsPaginator(1)
        itemsPaginator.set_page_size_limit(self.page_size_param)
        return itemsPaginator

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child Items results' streams."""

        item_number = record["numeroControlePncpCompra"]
        ids_context = extract_ids(item_number)
        ids_context["numeroItem"] = record["numeroItem"]
        return ids_context


class ItemResultsStream(PncpStream):
    """Items' results stream."""
    name = "pncp_item_results"

    path = "/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numeroItem}/resultados"
    primary_keys = ["numeroControlePNCPCompra", "numeroItem", "niFornecedor", "sequencialResultado"]
    replication_key = "dataAtualizacao"  # dataPublicacaoPncp
    schema_filepath = SCHEMAS_DIR / "item_result.json"
    records_jsonpath = "[*]"

    parent_stream_type = ItemsStream
    ignore_parent_replication_key = True


def extract_ids(purchase_control_id: str) -> dict:
    pattern = re.compile(r"(\d+)\-\d+\-(\d{6})\/(\d{4})", re.I)
    groups = re.findall(pattern, purchase_control_id)[0]

    return {
        "cnpj": groups[0],
        "sequencial": int(groups[1]),
        "ano": int(groups[2]),
    }

# def should_not_create_child_streams(purchase_control_id:str):
#     if purchase_control_id in created_purchase_streams:
#         return True
#     else:
#         return False

# def add_to_child_streams_control(purchase_control_id:str):
#     created_purchase_streams.append(purchase_control_id)
