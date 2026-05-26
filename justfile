import "~/.config/just/common.just"

default:
    @just --list

# запуск сервера "uv run uvicorn src.main:app --reload"
run:
    uv run uvicorn src.main:app --reload

# =========================
# DOCKER
# =========================



# Остановить и удалить volumes
down-v:
    docker compose down -v



# =========================
# SHELL
# =========================

# Shell FastAPI контейнера
#shell:
#    docker exec -it cloud_fastapi bash

# Shell Postgres
#shell-db:
#    docker exec -it cloud_postgres bash

# Postgres CLI
#psql:
#    docker exec -it cloud_postgres psql -U postgres

# =========================
# PYTHON
# =========================

# Тесты
#test:
#    docker exec -it cloud_fastapi pytest

# Форматирование
#format:
#    docker exec -it cloud_fastapi ruff format .

# Линтер
#lint:
#    docker exec -it cloud_fastapi ruff check .

# =========================
# ALEMBIC
# =========================

# Создать миграцию
#migrate name:
#    docker exec -it cloud_fastapi alembic revision --autogenerate -m "{{name}}"

# Применить миграции
#upgrade:
#    docker exec -it cloud_fastapi alembic upgrade head

# =========================
# DEBUG
# =========================

