import os
import re
from typing import Any, Callable, Optional, TypeVar, Union, cast

from flask import Flask, g
from pymysql import Connection
from pymysql.cursors import DictCursor

_NAME_TO_ENV = re.compile(r"[^A-Z0-9_]")


def connect(name: str):
    """Connects to a MySQL database resource using provided environment variables (e.g. `MYSQL_{name}_HOST`).

    :param name: name of MySQL resource as defined in chal.yaml
    :type name: str
    :return: pymysql connection object
    :rtype: pymysql.Connection
    """

    env_name = _NAME_TO_ENV.sub("", name.upper().replace("-", "_"))

    host = os.getenv(f"MYSQL_{env_name}_HOST")
    database = os.getenv(f"MYSQL_{env_name}_DB")
    user = os.getenv(f"MYSQL_{env_name}_USER")
    password = os.getenv(f"MYSQL_{env_name}_PASS")

    assert (
        host is not None
        and database is not None
        and user is not None
        and password is not None
    ), f"Environment variables for MySQL resource `{name}` not found (e.g. `MYSQL_{env_name}_HOST`)."

    return Connection(
        host=host,
        database=database,
        user=user,
        password=password,
        cursorclass=DictCursor,
    )


T = TypeVar("T")


def execute(
    connection: Connection,
    sql: str,
    values: Optional[Union[tuple, list]] = None,
    fetcher: Callable[[DictCursor], T] = lambda cursor: None,
):
    """Executes an SQL query against a database connection.

    :param connection: pymysql connection
    :type connection: Connection
    :param sql: SQL query to execute
    :type sql: str
    :param values: parametrised values, defaults to None
    :type values: tuple or list of values, optional
    :param fetcher: callback to execute with cursor to fetch results if any, defaults to `lambda cursor: None`
    :type fetcher: function taking a cursor and returning some result type, optional
    :return: return value of fetcher
    :rtype: return type of fetcher
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        return fetcher(cursor)


def fetch_one(connection: Connection, sql: str, values=None):
    """Executes an SQL query and calls `cursor.fetchone()` automatically."""
    return execute(connection, sql, values, fetcher=lambda cursor: cursor.fetchone())


def fetch_all(connection: Connection, sql: str, values=None):
    """Executes an SQL query and calls `cursor.fetchall()` automatically."""
    return execute(
        connection, sql, values, fetcher=lambda cursor: list(cursor.fetchall())
    )


class FlaskMySQL:
    """Flask extension to add basic transaction usage to requests. Each request gets a new connection but
    automatically commits or rolls back (if there is an unhandled exception) the entire transaction at
    the end of the request.
    """

    def __init__(self, name: str, app: Optional[Flask] = None):
        self.name = name

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        app.teardown_request(self._teardown_request)

    def _get_connections_dict(self):
        # g._connections is a dictionary of database names to connections.
        try:
            assert type(g._connections) is dict
            return g._connections
        except (AttributeError, AssertionError):
            g._connections = {}
            return g._connections

    def _get_connection(self):
        connections = self._get_connections_dict()
        if self.name not in connections:
            return None
        return cast(
            Connection,
            connections[self.name],
        )

    def _get_or_create_connection(self):
        db = self._get_connection()
        if db is None:
            db = connect(self.name)
            self._get_connections_dict()[self.name] = db
        return db

    def _teardown_request(self, exception: Optional[BaseException]):
        db = self._get_connection()

        if db is not None:
            if exception is None:
                db.commit()
                db.close()
            else:
                db.close()

            del self._get_connections_dict()[self.name]

    def execute(
        self,
        sql: str,
        values=None,
        fetcher: Callable[[DictCursor], T] = lambda cursor: None,
    ):
        """Executes an SQL query.

        :param sql: SQL query to execute
        :type sql: str
        :param values: parametrised values, defaults to None
        :type values: tuple or list of values, optional
        :param fetcher: callback to execute with cursor to fetch results if any, defaults to `lambda cursor: None`
        :type fetcher: function taking a cursor and returning some result type, optional
        :return: return value of fetcher
        :rtype: return type of fetcher
        """
        return execute(self._get_or_create_connection(), sql, values, fetcher)

    def fetch_one(self, sql: str, values=None):
        """Executes an SQL query and calls `cursor.fetchone()` automatically."""
        return fetch_one(self._get_or_create_connection(), sql, values)

    def fetch_all(self, sql: str, values=None) -> list[dict[str, Any]]:
        """Executes an SQL query and calls `cursor.fetchall()` automatically."""
        return fetch_all(self._get_or_create_connection(), sql, values)
