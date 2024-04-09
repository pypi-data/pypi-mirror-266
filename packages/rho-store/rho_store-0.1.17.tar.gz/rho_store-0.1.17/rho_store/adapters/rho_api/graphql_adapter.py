import secrets
from typing import Optional

import orjson
import requests
from requests.exceptions import RequestException

from rho_store.exceptions import RhoApiError, InvalidApiKey


class RhoApiGraphqlAdapter:
    REQUEST_TIMEOUT = 10.0

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

        self.session = requests.Session()

    def get_signed_url(self) -> tuple[str, str]:
        file_name = f"{secrets.token_hex(8)}.parquet"
        query = """
        mutation GetUploadUrl($fileName: String!) {
          getUploadUrl(fileName: $fileName) {
            ok
            errorCode
            url
            fileId
          }
        }
        """
        variables = {
            "fileName": file_name
        }
        data, errors = self._make_request(query, variables)
        if errors:
            raise RhoApiError(errors)
        mutation_result = data["getUploadUrl"]
        self._verify_mutation_result(mutation_result)
        url = mutation_result["url"]
        file_id = mutation_result["fileId"]
        return url, file_id

    def create_table(self, name: str) -> dict:
        query = """
        mutation CreateTable($data: CreateTableInput!) {
          createTable(data: $data) {
            ok
            errorCode
            table {
              id
              name
              workspaceId
            }
          }
        }
        """
        variables = {"data": {"name": name}}
        data, errors = self._make_request(query, variables)
        if errors:
            raise RhoApiError(errors)
        mutation_result = data["createTable"]
        self._verify_mutation_result(mutation_result)
        table = mutation_result["table"]
        return table

    def get_table(self, table_id: str) -> dict:
        query = """
        query GetTable($id: String!) {
          table(tableId: $id) {
            id
            name
            workspaceId
          }
        }
        """
        variables = {"id": table_id}
        data, errors = self._make_request(query, variables)
        if errors:
            raise RhoApiError(errors)
        return data.get("table")

    def process_file(
            self,
            file_id: str,
            table_id: str,
            strategy: Optional[str] = None,
            run_async: bool = True
    ) -> dict:
        query = """
        mutation ProcessFile ($data: ProcessFileInput!, $runAsync: Boolean) {
          processFile(data: $data, runAsync: $runAsync) {
            table {
              id
              name
            }
            ok
            errorCode
          }
        }
        """
        variables = {
            "data": {"fileId": file_id, "tableId": table_id, "strategy": strategy},
            "runAsync": run_async
        }
        data, errors = self._make_request(query, variables)
        if errors:
            raise RhoApiError(errors)
        mutation_result = data["processFile"]
        self._verify_mutation_result(mutation_result)
        table = mutation_result["table"]
        return table

    @staticmethod
    def _verify_mutation_result(mutation_result: dict):
        if not mutation_result["ok"]:
            error_code = mutation_result["errorCode"]
            raise RhoApiError(error_code)

    def _make_request(self, query: str, variables: dict = None) -> tuple[dict, dict]:
        payload = {"query": query, "operationName": self.get_operation_name(query)}
        if variables:
            payload["variables"] = variables
        headers = self.get_headers()
        response = self.session.post(
            self.base_url,
            json=payload,
            headers=headers,
            timeout=self.REQUEST_TIMEOUT
        )

        if response.status_code == 403:
            raise InvalidApiKey("Invalid API key")
        if response.status_code == 401:
            raise InvalidApiKey("No access")

        try:
            response.raise_for_status()
        except RequestException as e:
            # default
            raise RhoApiError(
                f"Bad response from server: {response.status_code}"
            ) from e

        # response_data = response.json()
        response_data = orjson.loads(response.content)
        data, errors = response_data.get("data"), response_data.get("errors")
        return data, errors

    def get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

    @staticmethod
    def get_operation_name(query: str) -> str:
        first_part = query.split("{")[0].strip()
        operation_name = first_part.split(" ")[1]
        if "(" in operation_name:
            operation_name = operation_name.split("(")[0]
        return operation_name.strip()


__all__ = ["RhoApiGraphqlAdapter"]
