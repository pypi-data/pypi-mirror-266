from dataclasses import field

from pydantic.dataclasses import dataclass

from ...utils import from_env

_HOST = "CASTOR_DATABRICKS_HOST"
_TOKEN = "CASTOR_DATABRICKS_TOKEN"  # noqa: S105


@dataclass
class DatabricksCredentials:
    """
    Credentials needed by Databricks client
    Requires:
    - host
    - token
    """

    host: str
    token: str = field(metadata={"sensitive": True})


def to_credentials(params: dict) -> DatabricksCredentials:
    """extract Databricks credentials"""
    host = params.get("host") or from_env(_HOST)
    token = params.get("token") or from_env(_TOKEN)
    return DatabricksCredentials(
        host=host,
        token=token,
    )
