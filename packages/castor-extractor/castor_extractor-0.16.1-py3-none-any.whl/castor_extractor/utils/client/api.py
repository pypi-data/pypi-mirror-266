import json
from typing import Optional

import requests

from ...warehouse.databricks.credentials import DatabricksCredentials

DEFAULT_TIMEOUT_MS = 30_000
APICredentials = DatabricksCredentials


class APIClient:
    """
    API client
    - used for Databricks Unity Catalog for now
    - authentication via access token for now
    """

    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self._timeout = DEFAULT_TIMEOUT_MS

    @staticmethod
    def build_url(host: str, path: str):
        if not host.startswith("https://"):
            host = "https://" + host
        return f"{host.strip('/')}/{path}"

    def _headers(self):
        return {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.credentials.token}",
        }

    def get(self, path: str, payload: Optional[dict] = None) -> dict:
        """
        path: REST API operation path, such as /api/2.0/clusters/get
        """
        url = self.build_url(self.credentials.host, path)
        response = requests.get(
            url,
            data=json.dumps(payload or dict()),
            headers=self._headers(),
            timeout=self._timeout,
        )

        if response.content:
            return json.loads(response.content)

        return {}
