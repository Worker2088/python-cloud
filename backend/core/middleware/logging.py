"""
Middleware для логирования HTTP-запросов.

Назначение:
- генерация request_id для каждого запроса
- измерение времени выполнения запроса
- логирование результата запроса (method, path, status_code, duration)
- проброс request_id в ContextVar для дальнейшего использования в логах
"""

import time
import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.request_context import (
    request_id_ctx_var,
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для трассировки HTTP-запросов.

    Функции:
    - создание request_id
    - установка request_id в ContextVar
    - замер latency запроса
    - логирование завершения запроса
    - добавление X-Request-ID в response headers
    """

    async def dispatch(self, request, call_next):
        """
        Обрабатывает каждый HTTP запрос.

        Flow:
        1. Генерация request_id
        2. Установка request_id в ContextVar
        3. Засекается время начала запроса
        4. Выполняется следующий middleware / endpoint
        5. Считается длительность запроса
        6. Логируется результат запроса
        7. Добавляется header X-Request-ID

        Returns:
            Response: HTTP ответ с добавленным request_id
        """

        request_id = str(uuid.uuid4())

        # Контекстная переменная с request_id (ContextVar)
        request_id_ctx_var.set(request_id)

        started = time.perf_counter()

        response = await call_next(request)

        duration = round(time.perf_counter() - started, 3)

        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
            },
        )

        response.headers["X-Request-ID"] = request_id

        return response
