# Облачное хранилище файлов на Django

стек **FastApi + PostgreSQL + MinIO + Redis**, полностью упакованное в **Docker Compose**.

## Быстрый старт

### Локальный запуск (через Docker Compose)

1. Убедитесь, что установлены **Docker** и **Docker Compose**.
2. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/Worker2088/python-cloud
    ```
3. Создайте файл `.env` на основе шаблона (если есть) или вручную задайте переменные окружения (см. раздел *Конфигурация*).
.env в корневую папку проекта
POSTGRES_USER=postgres
POSTGRES_PASSWORD=•••••••••••
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=cloud_db
JWT_EXPIRE_MINUTES=1200
JWT_SECRET=qwerty12345
REDIS_URL=redis://redis:6379
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET_NAME=user-files 

.env в папку frontend
VITE_BASE=/

5. Запустите стек контейнеров:
    ```bash
    docker compose up --build
    ```
5.  Откройте браузер: `http://localhost` 
6.  При первом запуске необходимо создать суперпользователя для доступа к админке Django:
    ```bash
    # Выполняется внутри контейнера app или через docker exec
    docker compose exec app python manage.py createsuperuser
    ```

### Остановка и очистка

*   **Остановить контейнеры (данные сохраняются в volumes):**
    ```bash
    docker compose down
    ```
*   **Полная очистка (удаляет все данные: БД, файлы в MinIO, сессии):**
    ```bash
    docker compose down -v
    ```

---

##