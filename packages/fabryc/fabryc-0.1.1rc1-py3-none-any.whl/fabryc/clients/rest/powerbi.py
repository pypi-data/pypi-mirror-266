from fabryc.clients.rest.base import BaseRestClient


class PowerBIRestClient(BaseRestClient):
    """Power BI REST client"""

    base_url = "https://api.powerbi.com/v1.0/myorg/"

    def get_groups(self, *args, **kwargs):
        endpoint = "groups"
        res = self.get(endpoint, *args, **kwargs)

        return res.json()["value"]

    def get_group_by_name(self, group_name: str) -> dict:

        params = {"$filter": f"name eq '{group_name}'"}
        group = self.get_groups(params=params)

        if len(group) == 0:
            raise Exception(f"Group {group_name} not found")

        return group[0]

    def get_datasets_in_workspace(self, workspace_id: str) -> list:
        endpoint = f"groups/{workspace_id}/datasets"
        res = self.get(endpoint)
        if not res.ok:
            print(res.reason)
            raise Exception(f"Failed to get datasets: {res.status_code}")
        return res.json()["value"]

    def _execute_queries(self, workspace_id: str, dataset_id: str, query: str):
        endpoint = f"groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
        payload = {"queries": [{"query": f"{query}"}]}

        print(payload)

        res = self.post(endpoint, payload=payload)

        if res.status_code != 200:
            print(res.reason)
            raise Exception(f"Failed to execute query: {res.status_code}")

        return res.json()["results"][0]["tables"][0]["rows"]
