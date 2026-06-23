"""
Модуль исключений storage-сервиса.

Содержит бизнес-исключения для работы с файловым хранилищем (S3/MinIO):
- конфликты имен
- ошибки доступа
- ошибки операций с папками/файлами
- внешние ошибки storage
"""

from src.auth.exception import BaseAppException


class ObjectAlreadyExistsError(BaseAppException):
    """
    Исключение: объект (файл или папка) уже существует в хранилище (HTTP 409).
    """

    def __init__(self, msg: str = "Папка/файл с таким именем уже существует") -> None:
        super().__init__(msg, 409)


class ParentFolderNotExistsError(BaseAppException):
    """
    Исключение: родительская папка не найдена (HTTP 404).
    """

    def __init__(self, msg: str = "Родительская папка не существует") -> None:
        super().__init__(msg, 404)


class FolderDeleteError(BaseAppException):
    """
    Ошибка удаления папки (HTTP 400).
    """

    def __init__(self, msg: str = "Не удалось удалить папку") -> None:
        super().__init__(msg, 400)


class FolderCopyError(BaseAppException):
    """
    Ошибка копирования папки (HTTP 400).
    """

    def __init__(self, msg: str = "Не удалось скопировать папку") -> None:
        super().__init__(msg, 400)


class ForbiddenError(BaseAppException):
    """
    Ошибка доступа: недостаточно прав для операции (HTTP 403).
    """

    def __init__(self, msg: str = "Недостаточно прав для выполнения действия") -> None:
        super().__init__(msg, 403)


class UnauthorizedError(BaseAppException):
    """
    Ошибка авторизации: пользователь не аутентифицирован (HTTP 401).
    """

    def __init__(self, msg: str = "Пользователь не авторизован") -> None:
        super().__init__(msg, 401)


class FolderNotFoundError(BaseAppException):
    """
    Папка не найдена (HTTP 404).
    """

    def __init__(self, msg: str = "Папка не найдена") -> None:
        super().__init__(msg, 404)


class ObjectNotFoundError(BaseAppException):
    """
    Объект (файл/папка) не найден в хранилище (HTTP 404).
    """

    def __init__(self, msg: str = "Ресурс не найден") -> None:
        super().__init__(msg, 404)


class InvalidPathError(BaseAppException):
    """
    Некорректный или небезопасный путь (валидация path) (HTTP 400).
    """

    def __init__(self, msg: str = "невалидный или отсутствующий путь") -> None:
        super().__init__(msg, 400)


class StorageExternalError(BaseAppException):
    """
    Ошибка внешнего хранилища (S3/MinIO/ботокор) (HTTP 500).
    """

    def __init__(self, msg: str = "Ошибка S3") -> None:
        super().__init__(msg, 500)
