FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем скрипт для создания суперпользователя
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
if not User.objects.filter(username='admin').exists(): \
    admin = User.objects.create_superuser('xaori', 'admin@example.com', 'password'); \
    admin.save();" > /app/create_superuser.py

# Объединяем команды в одну для уменьшения слоев
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python /app/create_superuser.py && python manage.py runserver 0.0.0.0:8000"]
