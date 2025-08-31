#########################
# api/Dockerfile
#########################

# ----------------------
# Общий базовый слой
# ----------------------
FROM python:3.12-slim AS base

# Не буферизируем вывод Python
ENV PYTHONUNBUFFERED=1

# Установка Poetry
RUN pip install --no-cache-dir poetry


# Рабочая директория
WORKDIR /app

# Копируем манифесты зависимостей
COPY pyproject.toml ./

# Предварительно загружаем зависимости Poetry для кеша
RUN poetry install --no-root --only main

# ----------------------
# Этап разработки
# ----------------------
FROM base AS dev

# Устанавливаем все зависимости (включая dev)
RUN poetry install --no-root

# Копируем код приложения
COPY . .

# Команды миграций и статики при старте
CMD ["sh", "-c", \
    "poetry run python manage.py migrate && \
     poetry run python manage.py runserver 0.0.0.0:8000"]

# ----------------------
# Этап продакшена
# ----------------------
FROM base AS prod

# Копируем код приложения
COPY . .

RUN poetry run python manage.py collectstatic --noinput

# Запуск — сначала миграции, потом uwsgi/uvicorn/gunicorn
CMD ["sh", "-c", "poetry run python manage.py migrate && poetry run uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --workers 2"]
