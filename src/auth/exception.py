from fastapi import HTTPException


class MyHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(404, "параметр менее 100")

class UserNotFoundError():
    pass
