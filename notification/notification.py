from typing import List

from django.db.models import QuerySet
from firebase_admin import messaging
from django.utils import timezone

from notification.models import FCMToken
from schedule.models import Client


BATCH_SIZE = 500  # ограничение FCM API

def send_notifications_by_clients(clients: QuerySet[Client]):
    messages = []
    token_map = []

    for client in clients:
        for token in client.fcm_tokens.all():
            messages.append(
                messaging.Message(
                    notification=messaging.Notification(
                        title=f"📅 Новое расписание для {client.client_name}",
                        body="Посмотри его в приложении",
                    ),
                    token=token.token,
                )
            )
            token_map.append(token.token)

            if len(messages) >= BATCH_SIZE:
                _send_batch(messages, token_map)
                messages.clear()
                token_map.clear()

    if messages:
        _send_batch(messages, token_map)


def _send_batch(messages: list[messaging.Message], token_map: list[str]):
    try:
        response = messaging.send_each(messages)
        print(f"✅ Отправлено {response.success_count}, ❌ ошибок {response.failure_count}")

        bad_tokens = []
        for i, resp in enumerate(response.responses):
            if not resp.success:
                if not resp.success:
                    bad_tokens.append(token_map[i])

        if bad_tokens:
            deleted_count, _ = FCMToken.objects.filter(token__in=bad_tokens).delete()
            print(f"🗑️ Удалено {deleted_count} невалидных токенов")

        good_tokens = [
            token_map[i] for i, r in enumerate(response.responses) if r.success
        ]
        if good_tokens:
            FCMToken.objects.filter(token__in=good_tokens).update(last_used_at=timezone.now())

    except Exception as e:
        print(f"🔥 Ошибка при отправке батча: {e}")
