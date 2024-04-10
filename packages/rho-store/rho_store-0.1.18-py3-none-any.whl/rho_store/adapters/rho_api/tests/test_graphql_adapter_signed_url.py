import json

import pytest
import responses

from rho_store.adapters import RhoApiGraphqlAdapter
from rho_store.exceptions import RhoApiError
from tests.utils import random_string


@responses.activate
def test_get_signed_link_returns_correct_url():
    # given
    base_url = "https://example.com/graphql"
    api_key = random_string()
    api_port = RhoApiGraphqlAdapter(base_url=base_url, api_key=api_key)
    signed_url = f"https://magic-link.com?key={random_string()}"
    file_id = random_string()
    mock_response = {"data": {"getUploadUrl": {"url": signed_url, "fileId": file_id, "ok": True, "errorCode": None}}}
    responses.post(base_url, json=mock_response, status=200)

    # when
    received_url, received_file_name = api_port.get_signed_url()

    # then
    assert received_url == signed_url
    assert received_file_name == file_id


@responses.activate
def test_get_signed_link_makes_correct_request():
    # given
    base_url = "https://example.com/graphql"
    api_key = random_string()
    api_port = RhoApiGraphqlAdapter(base_url=base_url, api_key=api_key)
    signed_url = f"https://magic-link.com?key={random_string()}"
    mock_response = {
        "data": {"getUploadUrl": {"url": signed_url, "fileId": "a_file_id", "ok": True, "errorCode": None}}
    }
    responses.post(base_url, json=mock_response, status=200)

    # when
    api_port.get_signed_url()

    # then
    last_request = responses.calls[0].request
    last_request_data = json.loads(last_request.body)
    assert "getUploadUrl" in last_request_data["query"]
    assert last_request_data["operationName"]
    auth_header = last_request.headers["X-Api-Key"]
    assert api_key in auth_header


@responses.activate
def test_get_signed_link_raises_exception_if_server_error():
    # given
    base_url = "https://example.com/graphql"
    api_key = random_string()
    api_port = RhoApiGraphqlAdapter(base_url=base_url, api_key=api_key)
    signed_url = f"https://magic-link.com?key={random_string()}"
    mock_response = {
        "data": {"getUploadUrl": {"url": signed_url, "fileId": "a_file_id", "ok": True, "errorCode": None}}
    }
    responses.post(base_url, json=mock_response, status=500)

    # when/then
    with pytest.raises(RhoApiError):
        api_port.get_signed_url()


@responses.activate
def test_get_signed_link_raises_exception_error_in_response_body():
    # given
    base_url = "https://example.com/graphql"
    api_key = random_string()
    api_port = RhoApiGraphqlAdapter(base_url=base_url, api_key=api_key)
    error_code = "BAD_REQUEST"
    mock_response = {"data": {"getUploadUrl": {"url": None, "ok": False, "errorCode": error_code}}}
    responses.post(base_url, json=mock_response, status=200)

    # when/then
    with pytest.raises(RhoApiError):
        api_port.get_signed_url()
