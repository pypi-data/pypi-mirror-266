from dataclasses import field
from typing import List, Optional

from pydantic.dataclasses import dataclass

from .constants import Urls


@dataclass
class Credentials:
    """Class to handle PowerBI rest API permissions"""

    client_id: str
    tenant_id: str
    secret: str = field(metadata={"sensitive": True})
    scopes: Optional[List[str]] = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [Urls.DEFAULT_SCOPE]
