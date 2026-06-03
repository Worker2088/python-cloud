import bcrypt
from typing import Protocol

# Контракт для хэшера
class IPasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...


class BcryptHasher():
    """
        Реализация хэширования паролей с использованием библиотеки bcrypt.
        """
    def __init__(self, rounds: int = 12) -> None:
        # rounds (work factor) определяет сложность/время вычисления хэша.
        # 12 — оптимальный баланс безопасности и скорости на сегодня.
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        # bcrypt работает исключительно с байтами (bytes),
        # поэтому сначала переводим строку пароля в байты через .encode()
        password_bytes = password.encode('utf-8')

        # Генерируем уникальную "соль" с заданным количеством раундов
        salt = bcrypt.gensalt(rounds=self.rounds)

        # Хэшируем и получаем байтовую строку хэша
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)

        # Переводим готовый хэш обратно в строку (str) для удобного сохранения в БД
        return hashed_bytes.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # Переводим входящий чистый пароль и хэш из базы в байты
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Функция hashpw сама извлечет соль из хэша базы и сравнит результаты
        return bcrypt.checkpw(plain_bytes, hashed_bytes)


