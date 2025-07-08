from typing import List
import firebase_admin
from firebase_admin import credentials, messaging


def send_notifications(clients):
    messages = []
    for client in clients:
        msg = messaging.Message(
            notification=messaging.Notification(
                title=f"📅 Появилось новое расписание для {client.client_name}",
                body="Посмотри его в приложении",
            ),
            topic=client.ascii_name,
        )
        messages.append(msg)
    try:
        response = messaging.send_each(messages)
    except Exception as e:
        print(f"🔥 Ошибка при отправке уведомлений: {e}")
        import traceback

        traceback.print_exc()
        return None

    return response
