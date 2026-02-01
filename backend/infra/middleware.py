import logging
import traceback

logger = logging.getLogger(__name__)


class ExceptionLoggingMiddleware:
    """Middleware to log full exception tracebacks to console."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Log the full traceback when an exception occurs."""
        logger.error(
            f"Exception in {request.method} {request.path}:\n"
            f"{traceback.format_exc()}"
        )
        return None

