from ninja import Router
from ninja.errors import HttpError

from notification.models import FCMToken
from notification.schema import FCMSchema
from schedule.models import Client

router = Router()


@router.post("/save_fcm_token/", summary="Сохранение токена в бд")
def save_fcm_token(request, token: FCMSchema):
    """Сохранение FCM токена в БД"""
    client = Client.objects.filter(client_name=token.client_name).first()
    if not client:
        raise HttpError(404, "Client not found")

    FCMToken.objects.create(
        token=token.fcm_token,
        client=client,
    )
    return {"status": "ok"}
