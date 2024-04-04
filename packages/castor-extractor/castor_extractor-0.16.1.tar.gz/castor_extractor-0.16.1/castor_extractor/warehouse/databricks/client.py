import logging
from datetime import date
from functools import partial
from typing import Any, Dict, List, Optional, Set

from ...utils import at_midnight, date_after
from ...utils.client.api import APIClient
from ...utils.pager import PagerOnToken
from ..abstract.time_filter import TimeFilter
from .credentials import DatabricksCredentials
from .format import DatabricksFormatter
from .types import TablesColumns

logger = logging.getLogger(__name__)


def _day_to_epoch_ms(day: date) -> int:
    return int(at_midnight(day).timestamp() * 1000)


def _day_hour_to_epoch_ms(day: date, hour: int) -> int:
    return int(at_midnight(day).timestamp() * 1000) + (hour * 3600 * 1000)


class DatabricksClient(APIClient):
    """Databricks Client"""

    def __init__(
        self,
        credentials: DatabricksCredentials,
        db_allowed: Optional[Set[str]] = None,
        db_blocked: Optional[Set[str]] = None,
    ):
        super().__init__(credentials)
        self._db_allowed = db_allowed
        self._db_blocked = db_blocked
        self.formatter = DatabricksFormatter()

    @staticmethod
    def name() -> str:
        return "Databricks"

    def _keep_catalog(self, catalog: str) -> bool:
        """
        Helper function to determine if we should keep the Databricks catalog
        which is a CastorDoc database
        """
        if self._db_allowed and catalog not in self._db_allowed:
            return False
        if self._db_blocked and catalog in self._db_blocked:
            return False
        return True

    def databases(self) -> List[dict]:
        path = "api/2.1/unity-catalog/catalogs"
        content = self.get(path=path)
        _databases = self.formatter.format_database(content.get("catalogs", []))
        return [d for d in _databases if self._keep_catalog(d["database_name"])]

    def _schemas_of_database(self, database: dict) -> List[dict]:
        path = "api/2.1/unity-catalog/schemas"
        payload = {"catalog_name": database["database_name"]}
        content = self.get(path=path, payload=payload)
        schemas = content.get("schemas", [])
        return self.formatter.format_schema(schemas, database)

    def schemas(self, databases: List[dict]) -> List[dict]:
        """
        Get the databricks schemas (also sometimes called databases)
        (which correspond to the schemas in Castor)
        leveraging the unity catalog API
        """
        return [
            schema
            for database in databases
            for schema in self._schemas_of_database(database)
        ]

    def _tables_columns_of_schema(self, schema: dict) -> TablesColumns:
        path = "api/2.1/unity-catalog/tables"
        payload = {
            "catalog_name": schema["database_id"],
            "schema_name": schema["schema_name"],
        }
        content = self.get(path=path, payload=payload)
        return self.formatter.format_table_column(
            content.get("tables", []), schema
        )

    def tables_and_columns(self, schemas: List[dict]) -> TablesColumns:
        """
        Get the databricks tables & columns leveraging the unity catalog API
        """
        tables: List[dict] = []
        columns: List[dict] = []
        for schema in schemas:
            t_to_add, c_to_add = self._tables_columns_of_schema(schema)
            tables.extend(t_to_add)
            columns.extend(c_to_add)
        return tables, columns

    @staticmethod
    def _time_filter(time_filter: Optional[TimeFilter]) -> dict:
        """time filter to retrieve Databricks' queries"""
        # define an explicit time window
        if not time_filter:
            time_filter = TimeFilter.default()

        assert time_filter  # for mypy

        hour_min = time_filter.hour_min
        hour_max = time_filter.hour_max
        day = time_filter.day
        if hour_min is not None and hour_max is not None:  # specific window
            start_time_ms = _day_hour_to_epoch_ms(day, hour_min)
            # note: in practice, hour_min == hour_max (hourly query ingestion)
            end_time_ms = _day_hour_to_epoch_ms(day, hour_max + 1)
        else:  # fallback to an extraction of the entire day
            start_time_ms = _day_to_epoch_ms(day)
            end_time_ms = _day_to_epoch_ms(date_after(day, 1))

        return {
            "filter_by": {
                "query_start_time_range": {
                    "end_time_ms": end_time_ms,
                    "start_time_ms": start_time_ms,
                }
            }
        }

    def query_payload(
        self,
        page_token: Optional[str] = None,
        max_results: Optional[int] = None,
        time_range_filter: Optional[dict] = None,
    ) -> dict:
        """helper method to build the payload used to retrieve queries"""
        # in payload: You can provide only one of 'page_token' or 'filter_by'
        if page_token:
            payload: Dict[str, Any] = {"page_token": page_token}
        else:
            if time_range_filter:
                payload = {**time_range_filter}
            else:
                payload = self._time_filter(None)  # default to yesterday
        if max_results:
            payload["max_results"] = max_results
        return payload

    def _scroll_queries(
        self,
        page_token: Optional[str] = None,
        max_results: Optional[int] = None,
        time_range_filter: Optional[dict] = None,
    ) -> dict:
        """
        Callback to scroll the queries api
        https://docs.databricks.com/api/workspace/queryhistory/list
        max_results: Limit the number of results returned in one page.
            The default is 100. (both on our side and Databricks')
        """
        path = "api/2.0/sql/history/queries"
        payload = self.query_payload(page_token, max_results, time_range_filter)
        content = self.get(path=path, payload=payload)
        return content if content else {}

    def queries(self, time_filter: Optional[TimeFilter] = None) -> List[dict]:
        """get all queries"""
        # add a time filter (by default: yesterday)
        time_range_filter = self._time_filter(time_filter)
        _time_filtered_scroll_queries = partial(
            self._scroll_queries,
            time_range_filter=time_range_filter,
        )

        # retrieve all queries using pagination
        raw_queries = PagerOnToken(_time_filtered_scroll_queries).all()

        return self.formatter.format_query(raw_queries)

    def users(self) -> List[dict]:
        """
        retrieve user from api
        """
        path = "api/2.0/preview/scim/v2/Users"
        content = self.get(path=path)
        return self.formatter.format_user(content.get("Resources", []))

    def _view_ddl(self, schema: dict) -> List[dict]:
        path = "api/2.1/unity-catalog/tables"
        payload = {
            "catalog_name": schema["database_id"],
            "schema_name": schema["schema_name"],
            "omit_columns": True,
        }
        content = self.get(path=path, payload=payload)
        return self.formatter.format_view_ddl(content.get("tables", []), schema)

    def view_ddl(self, schemas: List[dict]) -> List[dict]:
        """retrieve view ddl"""
        view_ddl: List[dict] = []
        for schema in schemas:
            v_to_add = self._view_ddl(schema)
            view_ddl.extend(v_to_add)
        return view_ddl
