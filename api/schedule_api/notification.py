from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json

# 1. Загрузка ключа
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
SERVICE_ACCOUNT_FILE = "service-account.json"  # путь к скачанному JSON

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# 2. Получаем токен
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
token = credentials.token

# 3. Формируем запрос
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json; UTF-8",
}

project_id = "schedule-app-kiteka"
url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

message = {
    "message": {
        "topic": "update",
        "notification": {
            "title": "Расписание обновлено!",
            "body": "Нажмите чтобы открыть приложение...",
        },
    }
}


def send_notification():
    response = requests.post(url, headers=headers, data=json.dumps(message))
    return response.status_code
