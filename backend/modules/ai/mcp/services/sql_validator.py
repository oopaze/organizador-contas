import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import DDL, DML, Keyword

from modules.ai.mcp.exceptions import (
    SqlNotAllowedError,
    SqlMultipleStatementsError,
)


ALLOWED_FIRST_TOKENS = {"SELECT", "WITH"}
# Token types that can appear as the leading keyword of a statement.
_LEADING_KEYWORD_TTYPES = (DML, DDL, Keyword, Keyword.CTE)


class SqlValidatorService:
    """Allowlist-based SQL validator. Rejects anything that is not a single
    SELECT (or WITH ... SELECT) statement. Strips comments so payloads cannot
    hide inside them. This is *defense-in-UX*: the Postgres role is the real
    security boundary.
    """

    def validate(self, query: str) -> str:
        if not query or not query.strip():
            raise SqlNotAllowedError("empty query")

        cleaned = sqlparse.format(
            query,
            strip_comments=True,
            keyword_case=None,
        ).strip()

        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].rstrip()

        if not cleaned:
            raise SqlNotAllowedError("query is empty after stripping comments")

        parsed = sqlparse.parse(cleaned)
        if len(parsed) > 1:
            raise SqlMultipleStatementsError(
                "only one statement is allowed per call"
            )

        statement: Statement = parsed[0]
        first_keyword = self._first_keyword(statement)
        if first_keyword is None or first_keyword.upper() not in ALLOWED_FIRST_TOKENS:
            raise SqlNotAllowedError(
                f"only SELECT/WITH statements are accepted (got: {first_keyword!r})"
            )

        self._reject_inner_dml_ddl(statement)
        return cleaned

    def _first_keyword(self, statement: Statement) -> str | None:
        for token in statement.tokens:
            if token.is_whitespace:
                continue
            if token.ttype in _LEADING_KEYWORD_TTYPES:
                return token.value
            if hasattr(token, "tokens"):
                inner = self._first_keyword(token)
                if inner is not None:
                    return inner
            return None
        return None

    def _reject_inner_dml_ddl(self, statement: Statement) -> None:
        forbidden = {
            "INSERT", "UPDATE", "DELETE", "MERGE", "TRUNCATE",
            "DROP", "ALTER", "CREATE", "GRANT", "REVOKE",
            "COPY", "VACUUM", "REINDEX",
        }
        for token in statement.flatten():
            if token.ttype in (DML, DDL, Keyword):
                if token.value.upper() in forbidden:
                    raise SqlNotAllowedError(
                        f"forbidden keyword inside query: {token.value!r}"
                    )
