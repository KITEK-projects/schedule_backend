FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем скрипт для запуска
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Используем entrypoint скрипт вместо прямого запуска
ENTRYPOINT ["./entrypoint.sh"]