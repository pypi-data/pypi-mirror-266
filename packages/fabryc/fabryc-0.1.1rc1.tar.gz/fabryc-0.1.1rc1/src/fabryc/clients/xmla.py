"""Class for interacting with the Power BI XMLA API."""

from fabryc.auth import get_token
from fabryc.setup import setup

setup()

# pylint: disable=import-error,wrong-import-position,wrong-import-order
import Microsoft.AnalysisServices.Tabular as TOM  # type: ignore


class XMLAClient:
    """Class for interacting with the Power BI XMLA API."""

    def __init__(self, token: str | None = None):
        if not token:
            token = get_token()

        self.xmla_connection_str = (
            "DataSource=powerbi://api.powerbi.com/v1.0/myorg/{workspace_name};"
            f"Password={token};"
        )

    def _get_connection_string(self, workspace_name: str):
        return self.xmla_connection_str.format(workspace_name=workspace_name)

    def get_server(self, workspace_name: str):
        """Return a `TOM.Server` object for the given workspace."""

        server = TOM.Server()
        server.Connect(self._get_connection_string(workspace_name))
        return server

    def get_database_by_name(self, workspace_name: str, database_name: str):
        server = self.get_server(workspace_name)
        return server.Databases.GetByName(database_name)

    def serialize_database_to_folder(
        self, workspace_name: str, database_name: str, dst: str
    ):
        database = self.get_database_by_name(workspace_name, database_name)
        TOM.TmdlSerializer.SerializeDatabaseToFolder(database, dst)
