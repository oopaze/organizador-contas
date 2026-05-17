import logging
import time

import psycopg2
from psycopg2 import errors as pg_errors
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from django.conf import settings

from modules.ai.mcp.domains.query_result import QueryResult
from modules.ai.mcp.domains.sql_query import SqlQuery
from modules.ai.mcp.exceptions import (
    SqlInvalidError,
    SqlPermissionDeniedError,
    SqlTimeoutError,
)
from modules.ai.mcp.factories.query_result import QueryResultFactory


logger = logging.getLogger("modules.ai.mcp")


class ReadOnlyPostgresGateway:
    """Holds a single psycopg2 connection authenticated as the read-only role.

    A new connection is opened lazily on first use and reused for the life of
    the MCP process. On any failure we close and re-open on the next call.
    """

    def __init__(self, query_result_factory: QueryResultFactory):
        self.query_result_factory = query_result_factory
        self._conn = None

    def _connect(self):
        db = settings.DATABASES["default"]
        conn = psycopg2.connect(
            host=db["HOST"],
            port=db["PORT"],
            dbname=db["NAME"],
            user=settings.MCP_DATABASE_USER,
            password=settings.MCP_DATABASE_PASSWORD,
            connect_timeout=5,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '5s'")
            cur.execute("SET idle_in_transaction_session_timeout = '5s'")
            cur.execute("SET lock_timeout = '2s'")
        return conn

    def _get_conn(self):
        if self._conn is None or self._conn.closed:
            self._conn = self._connect()
        return self._conn

    def execute(self, query: SqlQuery) -> QueryResult:
        conn = self._get_conn()
        started = time.monotonic()
        try:
            with conn.cursor() as cur:
                cur.execute(query.wrapped, query.params)
                return self.query_result_factory.from_cursor(
                    cur,
                    started_at_ms=int(started * 1000),
                    row_limit=1000,
                    now_ms=int(time.monotonic() * 1000),
                )
        except pg_errors.QueryCanceled as exc:
            self._reset()
            raise SqlTimeoutError("query exceeded 5s, add filters or aggregate") from exc
        except pg_errors.InsufficientPrivilege as exc:
            self._reset()
            raise SqlPermissionDeniedError(str(exc)) from exc
        except pg_errors.ReadOnlySqlTransaction as exc:
            self._reset()
            raise SqlPermissionDeniedError(
                "MCP connection is read-only"
            ) from exc
        except psycopg2.Error as exc:
            self._reset()
            raise SqlInvalidError(str(exc).strip()) from exc

    def execute_raw_for_test(self, sql: str) -> QueryResult:
        """Test-only escape hatch: run a raw SQL string with no wrapping."""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                if cur.description:
                    return self.query_result_factory.from_cursor(
                        cur, started_at_ms=0, row_limit=1000, now_ms=0
                    )
                return QueryResult(columns=[], rows=[], row_count=0,
                                   truncated=False, execution_ms=0)
        except pg_errors.InsufficientPrivilege as exc:
            self._reset()
            raise SqlPermissionDeniedError(str(exc)) from exc
        except pg_errors.ReadOnlySqlTransaction as exc:
            self._reset()
            raise SqlPermissionDeniedError("read-only transaction") from exc
        except psycopg2.Error as exc:
            self._reset()
            raise SqlInvalidError(str(exc).strip()) from exc

    def _reset(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def close(self):
        self._reset()
