#!/bin/bash

# Ждем, пока база данных будет доступна (если используется)
# python manage.py wait_for_db

# Применяем миграции
python manage.py migrate

# Инициализируем пользователей
python manage.py init_users

# Запускаем основной сервер
python manage.py runserver 0.0.0.0:8000