import bcrypt

def hash_password(password: str) -> str:
    """Хэширует чистый пароль."""
    # Переводим строку в байты
    pwd_bytes = password.encode('utf-8')
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хэшируем
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # Возвращаем строковое представление хэша для хранения в БД
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли чистый пароль с хэшем из БД."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )