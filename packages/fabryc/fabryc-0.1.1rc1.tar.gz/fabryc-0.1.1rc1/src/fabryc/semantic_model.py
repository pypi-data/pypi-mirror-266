""""
A class to represent a semantic model in Power BI.
"""

from collections import namedtuple
from pathlib import Path

import pandas as pd

from fabryc.auth import get_token
from fabryc.clients.rest import FabricRestClient, PowerBIRestClient
from fabryc.workspace import Workspace

Table = namedtuple(
    "Table",
    ["name", "is_hidden", "description"],
)

Relationship = namedtuple(
    "Relationship",
    ["from_table", "to_table", "from_cardinality", "to_cardinality"],
)


class SemanticModel:
    """A class to represent a semantic model in Power BI."""

    def __init__(
        self,
        workspace_name: str,
        dataset_name: str,
        token: str | None = None,
    ):
        if token is None:
            token = get_token()
        self.fabric_client = FabricRestClient(token)
        self.pbi_client = PowerBIRestClient(token)
        self.workspace_name = workspace_name
        self.dataset_name = dataset_name

        self.workspace = Workspace(workspace_name=workspace_name, token=token)
        self.model = self.workspace.get_database_by_name(self.dataset_name).Model

        self._set_tables()
        self._set_relationships()

    def __repr__(self) -> str:
        return f"SemanticModel(workspace='{self.workspace_name}', dataset='{self.dataset_name}')"

    def _set_tables(self):
        """Set all tables in the semantic model."""
        self.tables = [
            Table(
                name=table.Name,
                is_hidden=table.IsHidden,
                description=table.Description,
            )
            for table in self.model.Tables
        ]

    def get_tables(self) -> pd.DataFrame:
        """Gets all tables in the semantic model as a pandas DataFrame"""
        return pd.DataFrame(self.tables)

    def _set_relationships(self):
        """Gets all relationships in the semantic model."""
        self.relationships = [
            Relationship(
                from_table=relationship.FromTable.Name,
                to_table=relationship.ToTable.Name,
                from_cardinality=relationship.FromCardinality,
                to_cardinality=relationship.ToCardinality,
            )
            for relationship in self.model.Relationships
        ]

    def get_relationships(self) -> pd.DataFrame:
        """Gets all relationships in the semantic model as a pandas DataFrame"""
        return pd.DataFrame(self.relationships)

    def to_tmdl(self, path: str):
        """
        Exports the semantic model to a TMDL folder structure in the specified path.
        """
        Path(path).mkdir(exist_ok=True, parents=True)
        self.workspace.serialize_database_to_folder(self.dataset_name, folder_path=path)

    def to_pbi(self):
        """Exports the semantic model to PowerBI services"""
        raise NotImplementedError(
            "Exporting to PowerBI services is not yet implemented."
        )
