from ninja import NinjaAPI
from ninja.errors import HttpError
from django.http import HttpRequest

from datetime import datetime

from schedule_api.services import get_schedule_for_client


from .models import Client
from .schemas import ClientSchema


api = NinjaAPI()


def is_admin(user):
    return user.is_staff


@api.get("/clients/", response=list[str], summary="Получение клиентов")
def get_clients(request: HttpRequest, is_teacher: bool = False):
    "Получение списка клиентов по is_teacher"
    clientsDjangoModel = Client.objects.filter(is_teacher=is_teacher)
    clients = [i.client_name for i in clientsDjangoModel]
    return clients


@api.get("/schedule/", response=ClientSchema, summary="Получение расписания")
def get_schedule(request: HttpRequest, client_name: str):
    "Получение списка расписания по клиенту и времени"
    client_time_str = request.headers.get("X-CLIENT-TIME")

    if not client_time_str:
        raise HttpError(400, "Заголовок 'X-CLIENT-TIME' обязателен")

    try:
        client_time = datetime.fromisoformat(client_time_str).date()
    except ValueError:
        raise HttpError(400, "Некорректный формат 'X-CLIENT-TIME', ожидается ISO 8601")

    return get_schedule_for_client(client_name, client_time)
