"""
Контекст запроса (Request Context Storage).

Назначение:
- хранение request_id для текущего запроса
- хранение user_id для текущего пользователя
- используется для correlation logging (сквозная трассировка)

Основано на ContextVar (async-safe локальное хранилище контекста).
"""

from contextvars import ContextVar

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")
"""
Контекстная переменная request_id.

Содержит уникальный идентификатор запроса.
Используется для трассировки логов по цепочке вызовов.
"""

user_id_ctx_var: ContextVar[str] = ContextVar("user_id", default="-")
"""
Контекстная переменная user_id.

Содержит ID текущего авторизованного пользователя.
Используется для audit-логирования и безопасности.
"""
