import time

from starlette.requests import Request
from starlette.responses import Response

import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# тестовый модуль, чтобы посмотреть на работу middleware


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        logger.info(
            "START %s %s",
            request.method,
            request.url.path,
        )

        response = await call_next(request)

        elapsed = time.perf_counter() - start_time

        logger.info(
            "END %s %s status=%s time=%.3f",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )

        return response