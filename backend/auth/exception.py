"""
Модуль доменных исключений приложения.

Используется для:
- единообразной обработки ошибок
- централизованного exception handler в FastAPI
"""


class BaseAppException(Exception):
    """
    Базовое исключение приложения.

    Attributes:
        message: текст ошибки
        status_code: HTTP статус код
    """

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsError(BaseAppException):
    """Пользователь уже существует (HTTP 409)."""

    def __init__(self, msg: str = "Пользователь уже существует") -> None:
        super().__init__(msg, 409)


class UserNotLoggedInError(BaseAppException):
    """Пользователь не авторизован (HTTP 401)."""

    def __init__(self, msg: str = "Пользователь не авторизован") -> None:
        super().__init__(msg, 401)


class DatabaseError(BaseAppException):
    """Ошибка базы данных (HTTP 500)."""

    def __init__(self, msg: str = "Ошибка базы данных") -> None:
        super().__init__(msg, 500)


class UserNotFoundError(BaseAppException):
    """Пользователь не найден или неверные данные (HTTP 400)."""

    def __init__(
        self, msg: str = "Такого пользователя нет, или пароль неправильный"
    ) -> None:
        super().__init__(msg, 400)
