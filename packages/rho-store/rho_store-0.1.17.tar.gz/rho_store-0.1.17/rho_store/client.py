import time

import pandas as pd

from .adapters import RhoApiGraphqlAdapter, UploadFileHttpAdapter, DataTransportRestAdapter
from .config import init_config
from .exceptions import InvalidArgument
from .types import StoreDfResult, TableDataResult


class RhoClient:
    def __init__(self, api_key: str):
        self._config = init_config()
        self._api_port = RhoApiGraphqlAdapter(
            base_url=self._config.GRAPHQL_URL,
            api_key=api_key
        )
        self._file_upload_port = UploadFileHttpAdapter()
        self.data_transport_port = DataTransportRestAdapter(
            base_url=self._config.API_URL,
            api_key=api_key
        )

    def get_table_url(self, table_id: str, workspace_id: str) -> str:
        return f"{self._config.CLIENT_URL}/app/tables/{table_id}?wid={workspace_id}"

    def new_table(self, name: str) -> dict:
        table = self._api_port.create_table(name)
        return table

    def store_df(
            self,
            data: pd.DataFrame,
            name: str = None,
            table_id: str = None,
            strategy: str = None,
            run_async: bool = True
    ) -> StoreDfResult:

        if strategy:
            strategy = strategy.upper()
            self.validate_store_df_strategy(strategy)

        if table_id is None:
            if strategy != "NEW_TABLE":
                raise InvalidArgument(f"Cannot perform strategy {strategy} without a table_id")

        t1 = time.time()
        url, file_id = self._api_port.get_signed_url()
        t2 = time.time()
        self._file_upload_port.upload_dataframe(url, data)
        t3 = time.time()
        if table_id is None:
            if name is None:
                name = "New table"
            table = self._api_port.create_table(name)
            table_id = table["id"]
        else:
            table = self._api_port.get_table(table_id)

        t4 = time.time()
        self._api_port.process_file(file_id, table_id, strategy, run_async=run_async)
        t5 = time.time()
        print("- Get url: ", t2 - t1)
        print("- Upload file: ", t3 - t2)
        print("- Create table: ", t4 - t3)
        print("- Process file: ", t5 - t4)
        print("Total time: ", t5 - t1)

        workspace_id = table["workspaceId"]
        client_url = self.get_table_url(table_id, workspace_id)
        return StoreDfResult(
            table_id=table["id"],
            client_url=client_url
        )

    @staticmethod
    def validate_store_df_strategy(strategy: str):
        valid_strategies = {
            "NEW_TABLE",
            "NEW_VERSION",
            "APPEND",
            "MERGE",
        }
        if strategy not in valid_strategies:
            raise InvalidArgument(f"Invalid strategy: {strategy}")

    def store_data(self, data: list[dict]) -> StoreDfResult:
        df = pd.DataFrame(data)
        return self.store_df(df)

    def get_df(self, table_id: str) -> pd.DataFrame:
        result = self._get_table_data(table_id)
        parsed_data = pd.DataFrame(
            data=result.rows,
            columns=result.columns
        )
        df = self._remove_system_columns(parsed_data)
        return df

    def get_data(self, table_id: str) -> list[dict]:
        # TODO: Remove system columns?
        table_data = self._get_table_data(table_id)
        return table_data.to_list()

    def _get_table_data(self, table_id: str) -> TableDataResult:
        result = self.data_transport_port.get_table_data(table_id)
        return result

    @staticmethod
    def _remove_system_columns(df: pd.DataFrame) -> pd.DataFrame:
        system_columns = ["_id", "_version", "_created_at"]
        for system_column in system_columns:
            df.drop(columns=[system_column], inplace=True)
        return df


__all__ = ["RhoClient"]
