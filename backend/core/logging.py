"""
Logging filter для добавления контекстных данных в лог-записи.

Назначение:
- добавляет request_id из ContextVar
- добавляет user_id из ContextVar
- делает их доступными во всех логах без ручной передачи
"""

import logging

from backend.core.request_context import (
    request_id_ctx_var,
    user_id_ctx_var,
)


class RequestContextFilter(logging.Filter):
    """
    Filter для обогащения логов контекстной информацией.

    Добавляет:
    - request_id (из Request middleware)
    - user_id (из auth context)

    Используется в logging config через filters.
    """

    def filter(self, record):
        """
        Модифицирует LogRecord перед логированием.

        Args:
            record: стандартный LogRecord

        Returns:
            bool: всегда True (не фильтрует записи, только обогащает)
        """

        record.request_id = request_id_ctx_var.get()
        record.user_id = user_id_ctx_var.get()

        return True
