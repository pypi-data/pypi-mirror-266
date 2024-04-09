"""A client for the Microsoft Power BI Fabric API."""

import base64
import typing as t
from enum import StrEnum
from pathlib import Path

import requests

from fabryc.clients.rest.base import BaseRestClient


class ItemType(StrEnum):
    """The type of the item in a workspace."""

    DASHBOARD = "Dashboard"
    REPORT = "Report"
    SEMANTIC_MODEL = "SemanticModel"


class FabricRestClient(BaseRestClient):
    """Source: https://learn.microsoft.com/en-us/rest/api/fabric/articles/"""

    base_url = "https://api.fabric.microsoft.com/v1/"

    def list_items(self, workspace_id: str, type_: t.Optional[ItemType] = None) -> list:
        """Returns a list of items from the specified workspace.


        Source: https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items
        """
        path = f"workspaces/{workspace_id}/items"

        if type_:
            path += f"?type={type_}"

        res = requests.get(f"{self.base_url}{path}", timeout=60, headers=self.headers)

        return res.json()

    def export_item(self, workspace_id: str, item_id: str):
        """Exports the specified item from the specified workspace."""

        path = f"workspaces/{workspace_id}/items/{item_id}/getDefinition"

        url = f"{self.base_url}{path}"

        print(url)

        res = requests.post(url, timeout=60, headers=self.headers)

        if res.status_code not in (200, 202):
            print(f"Status code: {res.status_code}.")

        elif res.status_code == 202:
            print(res.json())
            print(res.headers)

        else:

            body = res.json()

            for part in body["definition"]["parts"]:
                print(f"Saving part: {part['path']}")

                output_dir = "test"

                output_filepath = Path(f"{output_dir}/{part['path']}")

                Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
                Path(output_filepath).touch()

                with open(output_filepath, "wb") as f:
                    f.write(base64.b64decode(part["payload"], validate=True))


if __name__ == "__main__":
    client = FabricRestClient()

    CORE_OPERATIONS_DEV_ID = "bd99c1c2-ac75-4bfa-839f-9223bd4c49e7"
    print(
        client.list_items(CORE_OPERATIONS_DEV_ID, type_=ItemType.SEMANTIC_MODEL),
    )
