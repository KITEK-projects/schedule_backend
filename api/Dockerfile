FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Объединяем команды в одну для уменьшения слоев
CMD ["sh", "-c", "python manage.py collectstatic && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
