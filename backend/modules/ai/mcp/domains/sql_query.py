from dataclasses import dataclass, field


@dataclass(frozen=True)
class SqlQuery:
    """A validated, user-scoped SQL query ready to be executed.

    `raw` is what the agent sent; `wrapped` is the version we execute (with
    CTEs that shadow real table names to enforce user_id and soft-delete
    filtering). `params` holds psycopg bind values.
    """

    raw: str
    wrapped: str
    params: dict = field(default_factory=dict)
