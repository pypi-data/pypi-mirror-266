import pytest
import responses

from rho_store.adapters import DataTransportRestAdapter
from rho_store.exceptions import FailedToGetData
from tests.utils import random_string


@responses.activate
def test_get_table_data_returns_correct_data():
    # given
    base_url = "https://api.com"
    api_key = random_string()
    data_port = DataTransportRestAdapter(base_url=base_url, api_key=api_key)
    mock_response = {"data": {"rows": [[1, 2], [3, 4]], "columns": ["id", "name"]}}
    table_id = random_string()
    url = data_port.get_url_for_table(table_id)
    responses.get(url, json=mock_response, status=200)

    # when
    result = data_port.get_table_data(table_id)

    # then
    assert result.table_id == table_id
    assert result.rows == mock_response["data"]["rows"]
    assert result.columns == mock_response["data"]["columns"]


@responses.activate
def test_get_table_data_makes_request_with_correct_header():
    # given
    base_url = "https://api.com"
    api_key = random_string()
    data_port = DataTransportRestAdapter(base_url=base_url, api_key=api_key)
    mock_response = {"data": {"rows": [[1, 2], [3, 4]], "columns": ["id", "name"]}}
    table_id = random_string()
    url = data_port.get_url_for_table(table_id)
    responses.get(url, json=mock_response, status=200)

    # when
    result = data_port.get_table_data(table_id)
    assert result

    # then
    last_request = responses.calls[0].request
    auth_header = last_request.headers["X-Api-Key"]
    assert api_key in auth_header


@responses.activate
def test_get_table_data_raises_exception_if_server_error():
    # given
    base_url = "https://api.com"
    api_key = random_string()
    data_port = DataTransportRestAdapter(base_url=base_url, api_key=api_key)
    mock_response = {"error": {"code": "BAD"}}
    table_id = random_string()
    url = data_port.get_url_for_table(table_id)
    responses.get(url, json=mock_response, status=500)

    # when/then
    with pytest.raises(FailedToGetData):
        data_port.get_table_data(table_id)
