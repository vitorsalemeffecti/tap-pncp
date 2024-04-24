from tap_pncp.helpers import ChildStreamControl, PncpBasePaginator, ItemsPaginator
from requests import Response

from unittest.mock import MagicMock, Mock, patch


def test_stream_control():
    streamControl = ChildStreamControl()
    assert len(streamControl.created_stream_ids) == 0
    assert streamControl.should_not_create('teste') == False

    streamControl.add_to_control('teste')
    assert len(streamControl.created_stream_ids) == 1
    assert streamControl.should_not_create('teste') == True


def test_paginator_returns_none():
    pncp_paginator = PncpBasePaginator(1)
    assert pncp_paginator.get_next(None) is None

    item_paginator = ItemsPaginator(1)
    assert item_paginator.get_next(None) is None


@patch('requests.Response')
def test_pncp_paginator_must_have_another_page(response_mock):
    response_mock.json.return_value = {'data': [], 'numeroPagina': 1, 'paginasRestantes': 1}

    pncp_paginator = PncpBasePaginator(1)
    next_page = pncp_paginator.get_next(response_mock)
    assert next_page is not None


@patch('requests.Response')
def test_pncp_paginator_must_not_have_another_page(response_mock):
    response_mock.json.return_value = {'data': [], 'numeroPagina': 1, 'paginasRestantes': 0}

    pncp_paginator = PncpBasePaginator(1)
    next_page = pncp_paginator.get_next(response_mock)
    assert next_page is None


@patch('requests.Response')
def test_item_paginator_must_have_another_page(response_mock):
    response_mock.json.return_value = [{'a': 0}, {'a': 0}, {'a': 0}, {'a': 0}, {'a': 0}, {'a': 0}, {'a': 0}, {'a': 0},
                                       {'a': 0}, {'a': 0}]

    item_paginator = ItemsPaginator(1)
    item_paginator.set_page_size_limit(10)
    next_page = item_paginator.get_next(response_mock)
    assert next_page is not None


@patch('requests.Response')
def test_item_paginator_must_not_have_another_page(response_mock):
    response_mock.json.return_value = [{'a': 0}, {'a': 0}, {'a': 0}, {'a': 0}, {'a': 0}]

    item_paginator = ItemsPaginator(1)
    item_paginator.set_page_size_limit(10)
    next_page = item_paginator.get_next(response_mock)
    assert next_page is None
