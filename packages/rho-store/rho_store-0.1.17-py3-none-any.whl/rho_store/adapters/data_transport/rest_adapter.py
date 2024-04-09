import logging

import orjson
import requests

from ...exceptions import FailedToGetData
from ...ports import DataTransportPort
from ...types import TableDataResult

logger = logging.getLogger(__name__)


class DataTransportRestAdapter(DataTransportPort):
    REQUEST_TIMEOUT = 15.0

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

        self.session = requests.Session()

    def get_table_data(self, table_id: str) -> TableDataResult:
        url = self.get_url_for_table(table_id)

        try:
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
        except requests.exceptions.RequestException as e:
            raise FailedToGetData("Failed to make request") from e

        if not response.ok:
            raise FailedToGetData(f"Failed to make request: {response.content}")

        response_data = orjson.loads(response.content)

        if data := response_data.get("data"):
            return TableDataResult(
                table_id=table_id,
                columns=data.get("columns", []),
                rows=data.get("rows", [])
            )

        logger.warning("Received response: %s", response_data)
        raise FailedToGetData(response_data.get("error"))

    def get_url_for_table(self, table_id: str) -> str:
        return f"{self.base_url}/v1/tables/{table_id}/data"

    def get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }


__all__ = ["DataTransportRestAdapter"]
