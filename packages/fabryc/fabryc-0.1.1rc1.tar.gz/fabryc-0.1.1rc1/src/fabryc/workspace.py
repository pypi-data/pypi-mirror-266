import pandas as pd

from fabryc.auth import get_token
from fabryc.clients.rest import FabricRestClient, PowerBIRestClient
from fabryc.clients.xmla import XMLAClient


class Workspace:

    def __init__(self, workspace_name: str, token: str | None = None):
        if not token:
            token = get_token()
        self.workspace_name = workspace_name
        self.xmla_client = XMLAClient(token)
        self.fabric_client = FabricRestClient(token)
        self.pbi_client = PowerBIRestClient(token)

        self.workspace_id = self.pbi_client.get_group_by_name(self.workspace_name)["id"]

    def get_datasets(self):
        datasets = self.pbi_client.get_datasets_in_workspace(self.workspace_id)
        return pd.DataFrame(datasets)

    def get_database_by_name(self, database_name: str):
        return self.xmla_client.get_database_by_name(self.workspace_name, database_name)

    def serialize_database_to_folder(self, database_name: str, folder_path: str):
        return self.xmla_client.serialize_database_to_folder(
            self.workspace_name, database_name, folder_path
        )
