from fastapi import HTTPException

class BaseAppException(Exception):
    pass

class MyHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(404, "параметр менее 100")


class UserAlreadyExists(BaseAppException):
    pass

class UserNotLogin(BaseAppException):
    pass

class DBError(BaseAppException):
    pass

class UserNotFound():
    pass
