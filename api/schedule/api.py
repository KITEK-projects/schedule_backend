from typing import Optional
from ninja import Header, Router
from ninja.errors import HttpError
from django.http import HttpRequest
from django.utils import timezone

from datetime import datetime

from app.auth import JWTAuth
from schedule.services import get_schedule_for_client

from .models import Client
from .schemas import ClientListSchema, ClientSchema

router = Router()
jwt_auth = JWTAuth()


def is_admin(user):
    return user.is_staff


@router.get(
    "/clients", response=ClientListSchema, summary="Получение клиентов", auth=jwt_auth
)
def get_clients(request: HttpRequest):
    "Получение списка клиентов (группы и учителя)"
    groups = Client.objects.filter(is_teacher=False)
    teachers = Client.objects.filter(is_teacher=True)
    return ClientListSchema(
        groups=[group.client_name for group in groups],
        teachers=[teacher.client_name for teacher in teachers],
    )


@router.get("", response=ClientSchema, summary="Получение расписания", auth=jwt_auth)
def get_schedule(
    request: HttpRequest,
    client_name: str,
    x_client_time: Optional[str] = Header(default=None, alias="X-CLIENT-TIME"),  # type: ignore
):
    "Получение списка расписания по клиенту и времени"

    if x_client_time:
        try:
            client_time = datetime.fromisoformat(x_client_time).date()
        except ValueError:
            raise HttpError(
                400, "Некорректный формат 'X-CLIENT-TIME', ожидается ISO 8601"
            )
    else:
        client_time = timezone.localdate()

    return get_schedule_for_client(client_name, client_time)
