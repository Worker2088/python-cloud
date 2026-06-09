

class BaseAppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserAlreadyExistsError(BaseAppException):
    def __init__(self, msg: str = "Пользователь уже существует") -> None:
        super().__init__(msg, 409)

class UserNotLoggedInError(BaseAppException):
    def __init__(self, msg: str = "Пользователь не авторизован") -> None:
        super().__init__(msg, 401)

class DatabaseError(BaseAppException):
    def __init__(self, msg: str = "Ошибка базы данных") -> None:
        super().__init__(msg, 500)

class UserNotFoundError(BaseAppException):
    def __init__(self, msg: str = "Пользователь не найден") -> None:
        super().__init__(msg, 404)