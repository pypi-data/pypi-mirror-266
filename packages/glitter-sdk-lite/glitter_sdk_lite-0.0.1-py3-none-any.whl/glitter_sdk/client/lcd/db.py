from __future__ import annotations

import requests
import base64
from glitter_sdk.exceptions import *
from glitter_sdk.util.url import urljoin
from glitter_proto.blockved.glitterchain.index import *
from glitter_sdk.util.parse_sql import to_glitter_arguments

__all__ = ["DB"]


class DB:
    def __init__(self, url):
        self.url = url

    def show_create_table(self, database: str, table: str):
        """
        Show the CREATE TABLE statement for an existing table.

        Args:
          database: The database name
          table: The table name

        Returns:
          The result containing the CREATE TABLE statement
        """
        endpoint = "/blockved/glitterchain/index/sql/show_create_table"
        req = ShowCreateTableRequest()
        req.database_name = database
        req.table_name = table
        r = requests.get(urljoin(self.url, endpoint), req.to_dict())
        if r.status_code != 200:
            raise LCDResponseError(message=r.text, response=r)
        response = ShowCreateTableResponse().from_dict(r.json())
        return response

    def list_databases(self, creator: str = None):
        """
        List all databases or filter by creator in glitter.

        Args:
        creator (optional): Only return databases created by this creator

        Returns:
        ListDatabasesResponse containing matching databases
        """

        endpoint = "/blockved/glitterchain/index/sql/list_databases"
        r = requests.get(urljoin(self.url, endpoint))
        if r.status_code != 200:
            raise LCDResponseError(message=str(r.status_code), response=r)

        result = SqlListDatabasesResponse()
        response = SqlListDatabasesResponse().from_dict(r.json())
        for db in response.databases:
            if creator and creator != db.creator:
                continue
            result.databases.append(db)
        return result

    def list_tables(self, table_keyword: str = None, uid: str = None, database: str = None,
                    page: int = None, page_size: int = None):
        """
        List tables in glitter, filtering by various criteria.

        Args:
          table_keyword: Filter tables by keyword
          uid: Filter tables by creator uid
          database: Filter tables by database name
          page: Page number for pagination
          page_size: Number of results per page

        Returns:
          ListTablesResponse containing matching tables
        """
        endpoint = "/blockved/glitterchain/index/sql/list_tables"

        payload = {}
        if table_keyword is not None:
            payload["keyword"] = table_keyword
        if uid is not None:
            payload["uid"] = uid
        if database is not None:
            payload["database"] = database
        if page is not None:
            payload["page"] = page
        if page_size is not None:
            payload["page_size"] = page_size

        r = requests.get(urljoin(self.url, endpoint), payload)
        if r.status_code != 200:
            raise LCDResponseError(message=str(r.status_code), response=r)
        return SqlListTablesResponse().from_dict(r.json())

    def query(self, sql: str, args: list = None):
        """
        Execute a SQL query statement.

        Args:
          sql: The SQL query string
          args: Optional list of arguments to substitute into the query

        Returns:
          A list of rows where each row is a dict mapping column name to value
        """
        endpoint = "/blockved/glitterchain/index/sql/simple_query"
        req = SqlQueryRequest()
        req.sql = sql
        if args is not None:
            req.arguments = to_glitter_arguments(args)
        r = requests.post(urljoin(self.url, endpoint), data=req.to_json(), timeout=20)
        if r.status_code != 200:
            raise LCDResponseError(message=r.text, response=str(r.status_code))
        response = SimpleSqlQueryResponse().from_dict(r.json())
        row_set = []
        for raw_row in response.result:
            row = {}
            for field_name, col_val in raw_row.row.items():
                value_type = col_val.column_value_type
                if value_type == ColumnValueType.IntColumn or value_type == ColumnValueType.UintColumn:
                    row[field_name] = int(col_val.value)
                elif value_type == ColumnValueType.FloatColumn:
                    row[field_name] = float(col_val.value)
                elif value_type == ColumnValueType.BoolColumn:
                    row[field_name] = bool(col_val.value)
                elif value_type == ColumnValueType.StringColumn:
                    row[field_name] = col_val.value
                elif value_type == ColumnValueType.BytesColumn:
                    row[field_name] = base64.standard_b64decode(col_val.value)
                elif value_type == ColumnValueType.InvalidColumn:
                    row[field_name] = col_val.value
            row_set.append(row)
        return row_set
