class MCPError(Exception):
    """Base class for MCP errors. Each subclass has a stable `code` that the
    MCP adapter surfaces to the agent.
    """

    code: str = "MCP_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class SqlNotAllowedError(MCPError):
    code = "SQL_NOT_ALLOWED"


class SqlMultipleStatementsError(MCPError):
    code = "SQL_MULTIPLE_STATEMENTS"


class SqlTimeoutError(MCPError):
    code = "SQL_TIMEOUT"


class SqlPermissionDeniedError(MCPError):
    code = "SQL_PERMISSION_DENIED"


class SqlInvalidError(MCPError):
    code = "SQL_INVALID"


class SchemaIntrospectionError(MCPError):
    code = "SCHEMA_INTROSPECTION_ERROR"
