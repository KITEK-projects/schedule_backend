# Бэкенд для сервиса "Приложение КИТЭКа"

В данном репозитори хранится бэкенд-состовляющая продукта "Приложение КИТЭКа"

## Стек

- [Django](https://www.djangoproject.com/)
- [Django ninja](https://django-ninja.dev/)
- [PostgreSQL](https://www.postgresql.org/)
- [Poetry](https://python-poetry.org/)
- [Redis](https://redis.io/)
- [Docker](https://www.docker.com/)


## Как запустить

**Для прода:**
```bash
docker compose --profile prod up --build
```

**Для разработки:**
```bash
docker compose --profile dev up --build
```

**Миграции:**
```bash
docker exec -it omsktec-api poetry run python manage.py makemigrations
docker exec -it omsktec-api poetry run python manage.py migrate
```

**Тесты:**
```bash
docker exec -it omsktec-api poetry run python manage.py test
```
