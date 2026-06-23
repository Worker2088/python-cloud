"""
Сервис бизнес-логики для работы с файловым хранилищем (S3-like storage).

Отвечает за:
- создание папок и файлов
- перемещение объектов
- удаление
- поиск
- получение структуры каталогов
- скачивание файлов и архивирование папок

Работает поверх абстракции репозитория (IStorageRepository).
"""

import io
import logging
import re
import zipfile

from src.auth.session.storage import ISessionStorage
from src.storage.exception import (
    InvalidPathError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    StorageExternalError,
)
from src.storage.interfaces import IStorageRepository
from src.storage.s3 import S3Client
from src.storage.schemas import StorageObjectSchema, ObjectType, DownloadResultDTO

logger = logging.getLogger(__name__)


class StorageService:
    """
    Основной сервис управления объектами в файловом хранилище пользователя.
    """

    def __init__(
        self,
        repo: IStorageRepository,
        session: ISessionStorage,
        s3_client: S3Client,
    ):
        """
        Инициализация сервиса.

        Args:
            repo: репозиторий для работы с S3/хранилищем
            session: слой хранения сессий пользователя
            s3_client: клиент S3
        """
        self.repo = repo
        self.session = session
        self.s3_client = s3_client

    async def create_folder(
        self, path: str, current_user_id: int
    ) -> StorageObjectSchema:
        """
        Создание папки и всех промежуточных директорий.

        Args:
            path: путь папки
            current_user_id: ID пользователя

        Returns:
            StorageObjectSchema: созданная папка
        """

        self._validate_path(path)

        folder_name, parent_parts = self._split_path_into_name_and_parent(path)
        base_path = f"user-{current_user_id}-files/"

        if await self.repo.object_exists(base_path + path):
            raise ObjectAlreadyExistsError("Папка уже существует")

        current_path = await self._create_parent_folders(
            base_path=base_path,
            folder_parts=parent_parts,
        )

        s3_key = f"{base_path}{current_path}{folder_name}/"

        await self.repo.put_object(s3_key, body=b"")

        return StorageObjectSchema(
            path=current_path,
            name=folder_name,
            type=ObjectType.DIRECTORY,
        )

    async def create_object(
        self, path: str, current_user_id: int, file: bytes
    ) -> list[StorageObjectSchema]:
        """
        Загрузка файла в хранилище.

        Args:
            path: относительный путь файла
            current_user_id: ID пользователя
            file: байты файла

        Returns:
            list[StorageObjectSchema]: созданный файл + метаданные папок
        """

        self._validate_path(path)

        base_path = f"user-{current_user_id}-files/"

        s3_key = f"{base_path}{path}"

        if await self.repo.object_exists(s3_key):
            raise ObjectAlreadyExistsError(f"Файл уже существует: {path}")

        await self.repo.put_object(key=s3_key, body=file)

        # 2. Формируем ответ для фронтенда.
        # ТЗ требует вернуть список объектов.
        # Обычно при загрузке файла логично вернуть только этот файл.
        # Но если ТЗ жестко требует возвращать структуру папок, нужно аккуратно распарсить путь.

        parts = path.split("/")
        filename = parts[-1]
        parent_path = "/".join(parts[:-1]) + "/" if len(parts) > 1 else ""

        result = []

        # Добавляем в ответ загруженный файл
        result.append(
            StorageObjectSchema(
                path=parent_path,
                name=filename,
                size=len(file),
                type=ObjectType.FILE,
            )
        )

        # создаем папки
        await self._create_parent_folders(
            base_path=base_path,
            folder_parts=parts[:-1],
        )

        current_path = ""
        for part in parts[:-1]:  # Проходим по всем папкам, кроме имени файла
            current_path += f"{part}/"

            # Добавляем в ответ папку
            result.append(
                StorageObjectSchema(
                    path=current_path.rsplit("/", 2)[0] or "",  # Путь к родителю
                    name=part + "/",
                    type=ObjectType.DIRECTORY,
                    size=None,
                )
            )

        return result

    async def move_object(
        self, from_path: str, to_path: str, current_user_id: int
    ) -> StorageObjectSchema:
        """
        Перемещение файла или папки внутри хранилища.

        Поддерживает рекурсивное копирование S3-объектов.

        Args:
            from_path: исходный путь
            to_path: новый путь
            current_user_id: ID пользователя

        Returns:
            StorageObjectSchema: перемещённый объект
        """

        self._validate_path(from_path)
        self._validate_path(to_path)

        # проверка, что не меняем тип объекта при перемещении
        if from_path.endswith("/") != to_path.endswith("/"):
            raise InvalidPathError()

        if to_path.startswith(from_path):
            raise InvalidPathError()

        object_name, parent_parts = self._split_path_into_name_and_parent(to_path)
        base_path = f"user-{current_user_id}-files/"

        current_path = await self._create_parent_folders(
            base_path=base_path,
            folder_parts=parent_parts,
        )

        # формирую ключи
        from_s3_key = f"{base_path}{from_path}"
        to_s3_key = f"{base_path}{current_path}{object_name}"

        if from_path.endswith("/"):
            to_s3_key = to_s3_key.rstrip("/") + "/"

        if not await self.repo.object_exists(from_s3_key):
            raise ObjectNotFoundError()

        if await self.repo.object_exists(to_s3_key):
            raise ObjectAlreadyExistsError("ресурс, лежащий по пути to уже существует")

        objects = await self.repo.get_list_objects(from_s3_key)

        copied = []

        try:
            for obj in objects:
                old_key = obj["Key"]
                relative = old_key[len(from_s3_key) :]
                new_key = to_s3_key + relative

                await self.repo.copy_object(old_key, new_key)
                copied.append((old_key, new_key))

            await self.repo.delete_list_objects(from_s3_key)

        except Exception as e:
            raise StorageExternalError()

        return StorageObjectSchema(
            path=current_path,
            name=object_name,
            size=await self.repo.size_file(to_s3_key),
            type=ObjectType.DIRECTORY if from_path.endswith("/") else ObjectType.FILE,
        )

    async def get_info_object(
        self, path: str, current_user_id: int
    ) -> list[StorageObjectSchema]:
        """
        Получение содержимого папки (файлы + директории).

        Args:
            path: путь папки
            current_user_id: ID пользователя

        Returns:
            list[StorageObjectSchema]: список объектов
        """
        # self._validate_path(path)
        base_path = f"user-{current_user_id}-files/"

        s3_key = f"{base_path}{path}"

        # получаем файлы и папки ТОЛЬКО 1 уровня (Delimiter="/")
        data = await self.repo.get_list_objects_with_delimiter(s3_key)
        objects = data.get("files", [])
        prefixes = data.get("dirs", [])

        result: list[StorageObjectSchema] = []

        # =========================
        # FOLDERS
        # =========================
        for item in prefixes:
            full_prefix = item.get("Prefix", "")  # "user-59-files/f0/"
            relative = full_prefix[len(s3_key) :]  # "f0/"

            if not relative:
                continue

            result.append(
                StorageObjectSchema(
                    path=path, name=relative, type=ObjectType.DIRECTORY, size=None
                )
            )

        # =========================
        # FILES
        # =========================
        for obj in objects:
            key = obj["Key"]  # "user-59-files/img.png"

            if key == s3_key:
                continue
            # получаем "img.png", из-за Delimiter не может быть "f0/img.png"
            relative = key[len(s3_key) :]

            if not relative:
                continue

            # доп проверка на наличие / в конце
            parts = relative.split("/")

            name = parts[0]

            result.append(
                StorageObjectSchema(
                    path=path,
                    name=name,
                    type=ObjectType.FILE,
                    size=obj.get("Size", 0),
                )
            )

        return result

    async def search_objects(
        self, current_user_id: int, query: str
    ) -> list[StorageObjectSchema]:
        """
        Поиск файлов и папок пользователя.

        Args:
            current_user_id: ID пользователя
            query: строка поиска

        Returns:
            list[StorageObjectSchema]: найденные объекты
        """
        self._validate_path(query)

        base_path = f"user-{current_user_id}-files/"
        objects = await self.repo.get_list_objects(base_path)

        q = query.lower().strip()
        result = []

        for obj in objects:
            key = obj["Key"]

            name, path, is_dir = self._parse_s3_key(base_path, key)

            if not name:
                continue

            full_search_string = f"{path}{name}" if not is_dir else f"{path}{name}/"

            if q not in full_search_string.lower():
                continue

            if q not in name:
                continue

            if is_dir:
                result.append(
                    StorageObjectSchema(
                        path=path,
                        name=name + "/",
                        type=ObjectType.DIRECTORY,
                    )
                )
            else:
                size = await self.repo.size_file(base_path + path + name)

                result.append(
                    StorageObjectSchema(
                        path=path,
                        name=name,
                        size=size,
                        type=ObjectType.FILE,
                    )
                )

        return result

    async def download_object(
        self, current_user_id: int, path: str
    ) -> DownloadResultDTO:
        """
        Скачивание файла или папки.

        Папки архивируются в ZIP.

        Args:
            current_user_id: ID пользователя
            path: путь объекта

        Returns:
            DownloadResultDTO: файл или архив
        """
        self._validate_path(path)

        base = f"user-{current_user_id}-files/"
        s3_key = base + path

        is_folder = path.endswith("/")

        # ======================
        # FILE
        # ======================
        if not is_folder:
            file_bytes = await self.repo.get_object(s3_key)

            return DownloadResultDTO(
                content=file_bytes,
                filename=path.split("/")[-1],
                media_type="application/octet-stream",
            )

        # ======================
        # FOLDER -> ZIP
        # ======================

        objects = await self.repo.get_list_objects(s3_key)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for obj in objects:
                key = obj["Key"]

                relative_path = key.replace(s3_key, "", 1)

                # отсекаем root папку
                if not relative_path:
                    continue

                data = await self.repo.get_object(key)

                zip_file.writestr(relative_path, data)

        zip_buffer.seek(0)

        return DownloadResultDTO(
            content=zip_buffer.getvalue(),
            filename=path.rstrip("/").split("/")[-1] + ".zip",
            media_type="application/zip",
        )

    async def delete_object(self, path: str, current_user_id: int) -> None:
        """
        Удаление файла или папки.

        Args:
            path: путь объекта
            current_user_id: ID пользователя
        """
        self._validate_path(path)

        base_path = f"user-{current_user_id}-files/"

        s3_key = f"{base_path}{path}"

        if not path.endswith("/"):
            obj = await self.repo.object_exists(s3_key)

            if not obj:
                raise ObjectNotFoundError("404 сервис delete_object")

            await self.repo.delete_object(s3_key)
        else:
            await self.repo.delete_list_objects(s3_key)

    def _validate_path(self, path: str) -> None:
        """
        Валидация пути объекта.

        Запрещает:
        - переходы вверх по директориям (..)
        - двойные слэши
        - недопустимые символы
        """

        if ".." in path:
            raise InvalidPathError()

        if "//" in path:
            raise InvalidPathError()

        pattern = r"^[a-zA-Z0-9_\-./]+$"

        if not re.match(pattern, path):
            raise InvalidPathError()

    def _parse_s3_key(self, prefix: str, key: str) -> tuple[str, str, bool]:
        """
        Парсинг S3 ключа в (имя, путь, тип объекта).

        Returns:
            tuple[str, str, bool]: name, path, is_dir
        """

        relative_key = key.replace(prefix, "", 1)

        is_dir = relative_key.endswith("/")

        parts = (
            relative_key.rstrip("/").split("/") if is_dir else relative_key.split("/")
        )

        name = parts[-1]
        path = "/".join(parts[:-1])

        if path:
            path += "/"

        return name, path, is_dir

    def _split_path_into_name_and_parent(self, path: str):
        """
        Разделяет путь на имя объекта и родительские директории.

        Returns:
            tuple: (folder_name, parent_parts)
        """
        clean_path = path.strip("/")

        parts = clean_path.split("/")

        folder_name = parts[-1]

        parent_parts = parts[:-1]

        return folder_name, parent_parts

    async def _create_parent_folders(
        self,
        base_path: str,
        folder_parts: list[str],
    ) -> str:
        """
        Создает цепочку промежуточных папок.

        Пример:
            folder_parts = ["docs", "work", "reports"]

        Создаст:
            docs/
            docs/work/
            docs/work/reports/

        Returns:
            str: путь последней созданной папки
        """

        current_path = ""

        for part in folder_parts:
            current_path += f"{part}/"

            folder_key = base_path + current_path

            if not await self.repo.object_exists(folder_key):
                await self.repo.put_object(folder_key, body=b"")

        return current_path
