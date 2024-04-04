import asyncio
from typing import Dict, Any

from lunar.config import Config
from lunar.lunar_client import LunarClient

loop = asyncio.get_event_loop()


class DynamodbClient(LunarClient):
    """
    Client for BAP Data API (`/v1/dynamodb`).

    ## Example

    ```python
    import bap

    client = bap.client("dynamodb")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def get_target_table_count_async(
        self,
        table_name: str,
    ) -> int:
        """
        Get a count of target table (async).

        ## Args

        - table_name: (str) Name of table

        ## Returns
        int

        ## Example

        ```python
        data = await client.get_target_table_count_async(
            table_name="my_target_table"
        )
        ```
        """

        body = await self._request(method="GET", url=f"{self.config.API_PATH}/target_tables/{table_name}")
        return body["data"]["count"]

    def get_target_table_count(
        self,
        table_name: str,
    ) -> int:
        """
        Get a count of target table (async).

        ## Args

        - table_name: (str) Name of table

        ## Returns
        int

        ## Example

        ```python
        data = client.get_target_table_count(
            table_name="my_target_table"
        )
        ```
        """

        return loop.run_until_complete(self.get_target_table_count_async(table_name=table_name))

    async def delete_target_table_async(self, table_name: str, force: bool = None) -> Dict[str, Any]:
        """
        Delete a target table (async). It raises error if the table is not empty.
        You can use force option if you want to delete it anyway.

        ## Args

        - table_name: (str) Name of table

        ## Returns
        dict

        ## Example

        ```python
        data = await client.delete_target_table_async(
            table_name="my_target_table", force=True
        )
        ```
        """
        params = {"force": "true"} if force else {}

        body = await self._request(
            method="DELETE", url=f"{self.config.API_PATH}/target_tables/{table_name}", params=params
        )

        return body["data"]

    def delete_target_table(self, table_name: str, force: bool = None) -> Dict[str, Any]:
        """
        Delete a target table. It raises error if the table is not empty.
        You can use force option if you want to delete it anyway.

        ## Args

        - table_name: (str) Name of table

        ## Returns
        dict

        ## Example

        ```python
        data = client.delete_target_table(
            table_name="my_target_table", force=True
        )
        ```
        """

        return loop.run_until_complete(self.delete_target_table_async(table_name=table_name, force=force))
