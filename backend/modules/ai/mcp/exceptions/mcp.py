class MCPError(Exception):
    """Base class for MCP errors. Each subclass has a stable `code` that the
    MCP adapter surfaces to the agent.
    """

    code: str = "MCP_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidCategoryError(MCPError):
    code = "INVALID_CATEGORY"


class InvalidDateError(MCPError):
    code = "INVALID_DATE"


class InvalidParamError(MCPError):
    code = "INVALID_PARAM"
