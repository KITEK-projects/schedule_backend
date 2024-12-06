#!/bin/bash

# Ждем, пока база данных будет доступна (если используется)
# python manage.py wait_for_db

python manage.py makemigrations

# Применяем миграции
python manage.py migrate

# Запускаем основной сервер
python manage.py runserver 0.0.0.0:8000