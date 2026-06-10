from sqlalchemy import String, Boolean, ForeignKey, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Folder(Base):
    """
    Модель хранилища.
    """
    __tablename__ = "folders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True
    )

    # Ограничение: имена папок должны быть уникальны внутри одной родительской папки и для одного юзера
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', 'user_id', name='uq_folder_unique_name'),
        Index('ix_folders_user_parent', 'user_id', 'parent_id')
    )

    # Прямая связь: у папки есть дети (другие папки)
    children: Mapped[list["Folder"]] = relationship(
        "Folder",
        foreign_keys=[parent_id],
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"  # Оптимизация: подгружает детей одним дополнительным запросом, а не N+1
    )

    # Обратная связь: у дочерней папки есть папка-родитель
    parent: Mapped["Folder | None"] = relationship(
        "Folder",
        remote_side=[id],
        back_populates="children",
        lazy="joined" # Для родителя обычно удобно загружать сразу
    )

    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class File(Base):
    """
    Модель хранилища.
    """
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    folder_id: Mapped[int] = mapped_column(ForeignKey("folders.id"), nullable=True)

    name: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False
    )

    s3_key: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False
    )
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        # Уникальность имени файла внутри папки и для юзера (опционально, зависит от бизнес-логики)
        UniqueConstraint('name', 'folder_id', 'user_id', name='uq_file_unique_name'),
        # индекс для быстрого поиска файлов в папке
        Index('ix_files_user_folder', 'user_id', 'folder_id'),
        Index('ix_files_s3_key', 's3_key')  # Важно для поиска файла по ключу S3
    )

    folder: Mapped["Folder"] = relationship(
        "Folder",  # На какой класс ссылаемся (Folder)
        back_populates="files",  # Имя обратной связи в классе Folder
        foreign_keys=[folder_id],  # Явно говорим: связь идет через колонку folder_id
        lazy="joined"  # Сразу загружать папку при загрузке файла (JOIN)
    )








# Soft Delete (Мягкое удаление). Вместо физического удаления строк из БД (и последующего вызова S3), добавьте колонку is_deleted: bool и deleted_at: datetime.
#
# Пользователь нажимает “Удалить”. Вы ставите флаг. Файл исчезает из интерфейса.
#
# Через 30 дней фоновый процесс окончательно удаляет запись из БД и объект из S3. Это спасает от случайных удалений.


# Row Level Security (RLS) в Postgres. Если используете PostgreSQL, включите RLS. Это позволит базе данных самой отвергать запросы к чужим данным на уровне SQL, даже если ваш код ошибся в проверке user_id.


# ВАЖНО!
# Транзакции. Операции создания папки/файла должны быть обернуты в транзакцию. Если создание записи в БД прошло, а загрузка в S3 упала — транзакция должна откатить запись в БД.




