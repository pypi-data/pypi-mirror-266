import logging
from datetime import datetime
from typing import List, Optional

from .types import TablesColumns

logger = logging.getLogger(__name__)

EXCLUDED_DATABASES = {"system"}
EXCLUDED_SCHEMAS = {"information_schema", "default"}


def _to_datetime_or_none(time_ms: Optional[int]) -> Optional[datetime]:
    """return time in ms as datetime or None"""
    if not time_ms:
        return None
    return datetime.fromtimestamp(time_ms / 1000.0)


def _table_payload(schema: dict, table: dict) -> dict:
    return {
        "id": table["table_id"],
        "schema_id": f"{schema['id']}",
        "table_name": table["name"],
        "description": table.get("comment"),
        "tags": [],
        "type": table.get("table_type"),
    }


def _column_payload(table: dict, column: dict) -> dict:
    return {
        "id": f"`{table['id']}`.`{column['name']}`",
        "column_name": column["name"],
        "table_id": table["id"],
        "description": column.get("comment"),
        "data_type": column["type_name"],
        "ordinal_position": column["position"],
    }


class DatabricksFormatter:
    """
    Helper functions.
    Format the response in the format to be exported as csv
    """

    @staticmethod
    def format_database(raw_databases: List[dict]) -> List[dict]:
        databases = []
        for catalog in raw_databases:
            name = catalog["name"]
            if name in EXCLUDED_DATABASES:
                continue
            db = {
                "id": name,
                "database_name": name,
            }
            databases.append(db)
        return databases

    @staticmethod
    def format_schema(raw_schemas: List[dict], database: dict) -> List[dict]:
        schemas = []
        for schema in raw_schemas:
            if schema["name"] in EXCLUDED_SCHEMAS:
                continue
            sc = {
                "id": schema["full_name"],
                "database_id": database["id"],
                "schema_name": schema["name"],
                "description": schema.get("comment"),
                "tags": [],
            }
            schemas.append(sc)
        return schemas

    @staticmethod
    def format_table_column(
        raw_tables: List[dict], schema: dict
    ) -> TablesColumns:
        tables = []
        columns = []
        if not raw_tables:
            return [], []
        for table in raw_tables:
            t = _table_payload(schema, table)
            tables.append(t)
            if not table.get("columns"):
                continue
            for column in table["columns"]:
                c = _column_payload(t, column)
                columns.append(c)

        return tables, columns

    @staticmethod
    def format_query(raw_queries: List[dict]) -> List[dict]:
        queries = []
        for q in raw_queries:
            if not q["query_text"]:
                continue
            start_time = _to_datetime_or_none(q.get("query_start_time_ms"))
            end_time = _to_datetime_or_none(q.get("query_end_time_ms"))
            query = {
                "query_id": q["query_id"],
                "database_id": None,
                "database_name": None,
                "schema_name": None,
                "query_text": q["query_text"],
                "user_id": q["user_id"],
                "user_name": q["user_name"],
                "start_time": start_time,
                "end_time": end_time,
            }
            queries.append(query)
        return queries

    @staticmethod
    def _primary(emails: List[dict]) -> Optional[str]:
        """helper function to select a unique email"""
        if not emails:
            return None
        for email in emails:
            if email.get("primary", False):
                return email["value"]
        return emails[0]["value"]

    def format_user(self, raw_users: List[dict]) -> List[dict]:
        users = []
        for user in raw_users:
            users.append(
                {
                    "id": user["id"],
                    "email": self._primary(user["emails"]),
                    "first_name": None,
                    "last_name": user.get("displayName") or user["userName"],
                    "user_name": user["userName"],
                }
            )
        return users

    @staticmethod
    def format_view_ddl(tables: List[dict], schema: dict) -> List[dict]:
        view_ddl: List[dict] = []
        if not tables:
            return view_ddl
        for table in tables:
            if not table.get("view_definition"):
                continue
            view_ddl.append(
                {
                    "database_name": schema["database_id"],  # db id = name
                    "schema_name": schema["schema_name"],
                    "view_name": table["name"],
                    "view_definition": table["view_definition"],
                }
            )

        return view_ddl
