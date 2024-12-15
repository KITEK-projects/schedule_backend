#!/bin/bash


python manage.py makemigrations

# Применяем миграции
python manage.py migrate

# Запускаем основной сервер
python manage.py runserver 0.0.0.0:8000