from src.auth.exception import BaseAppException


class FolderAlreadyExistsError(BaseAppException):
    def __init__(self, msg: str = "Папка с таким именем уже существует") -> None:
        super().__init__(msg, 409)


class FolderDeleteError(BaseAppException):
    def __init__(self, msg: str = "Не удалось удалить папку") -> None:
        super().__init__(msg, 400)


class ForbiddenError(BaseAppException):
    def __init__(self, msg: str = "Недостаточно прав для выполнения действия") -> None:
        super().__init__(msg, 403)


class FolderNotFoundError(BaseAppException):
    def __init__(self, msg: str = "Папка не найдена") -> None:
        super().__init__(msg, 404)





