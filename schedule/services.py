from datetime import datetime, date
from typing import List
from django.db import transaction
from django.db.models import QuerySet
from django.utils.timezone import localtime
from schedule.models import Client, Lesson, ScheduleDay, ScheduleFile, Bell
from schedule.parsers import html_parse
from schedule.schemas import (
    ClientSchema,
    LessonItemSchema,
    LessonSchema,
    ScheduleDaySchema,
)
from notification.notification import send_notifications_by_clients
from ninja.errors import HttpError

from schedule.urls import is_lower_course


def get_schedule_for_client(client_name: str, client_time: date) -> ClientSchema:
    schedule_bells = BellService()
    scheduleDays: QuerySet[ScheduleDay] = ScheduleDay.objects.filter(
        client__client_name=client_name
    )
    client = Client.objects.filter(client_name=client_name).first()

    if client is None:
        raise HttpError(404, "Client not found")

    last_update_local = localtime(client.last_update).isoformat()

    data = ClientSchema(
        client_name=client.client_name,
        last_update=last_update_local,
        schedules=[],
    )

    for scheduleDay in scheduleDays:
        if scheduleDay.date < client_time:
            continue

        date = scheduleDay.format_date
        week_day = scheduleDay.week_day
        lessons: List[LessonSchema] = []

        for lesson in scheduleDay.lessons.all():
            # Ищем существующий урок с таким номером
            local_lesson = next(
                (obj for obj in lessons if obj.number == lesson.number), None
            )
            # Если урока нет - создаем новый и добавляем в список
            if local_lesson is None:
                local_lesson = LessonSchema(
                    number=lesson.number,
                    time=schedule_bells.get_bell_text(
                        lesson_number=lesson.number,
                        weekday=week_day,
                        client_name=(
                            lesson.partner if client.is_teacher else client.client_name
                        ),
                    ),
                    items=[],
                )
                lessons.append(local_lesson)

            # Добавляем информацию об уроке
            local_lesson.items.append(
                LessonItemSchema(
                    title=lesson.title,
                    type=lesson.type,
                    partner=lesson.partner,
                    location=lesson.location or "",
                )
            )

        data.schedules.append(
            ScheduleDaySchema(
                date=date,
                week_day=week_day,
                lessons=sorted(lessons, key=lambda x: x.number),
            )
        )

    if len(data.schedules) == 0:
        data.schedules.append(
            ScheduleDaySchema(
                date=client_time.strftime("%Y-%m-%d"),
                week_day=client_time.weekday(),
                lessons=[],
            )
        )

    return data


@transaction.atomic
def set_schedule(content, uploaded_file, is_send_notifications: bool):
    clients = []

    parsed_data = html_parse(content)

    for item in parsed_data:
        client, _ = Client.objects.get_or_create(
            client_name=item["client_name"],
            is_teacher=item["is_teacher"],
        )
        clients.append(client)
        for schedule in item["schedules"]:
            scheduleDay, _ = ScheduleDay.objects.get_or_create(
                date=datetime.fromisoformat(schedule["date"]).date(),
                client=client,
            )

            scheduleDay.lessons.all().delete()

            Lesson.objects.bulk_create(
                [
                    Lesson(
                        schedule=scheduleDay,
                        number=lesson["number"],
                        title=lesson["title"],
                        type=lesson["type"],
                        partner=lesson["partner"],
                        location=lesson.get("location", ""),
                    )
                    for lesson in schedule["lessons"]
                ]
            )

        client.update_last_modified()

    if is_send_notifications:
        client_ids = [c.id for c in clients]
        clients_with_tokens = Client.objects.filter(id__in=client_ids).prefetch_related("fcm_tokens")

        send_notifications_by_clients(clients_with_tokens)

    ScheduleFile.objects.create(
        file_name=uploaded_file.name,
        schedule_file=uploaded_file,
    )


class BellService:
    @staticmethod
    def get_schedule_code(weekday: int, is_lower_course: bool) -> str:
        """
        Определяет код расписания на основе входных данных.
        Weekday: 0=Mon, ..., 5=Sat, 6=Sun
        """
        prefix = "lower" if is_lower_course else "upper"

        if weekday == 0:
            suffix = "mon"
        elif weekday == 5:
            suffix = "sat"
        else:
            suffix = "std"

        return f"{prefix}_{suffix}"

    @staticmethod
    def get_bell_text(lesson_number: int, weekday: int, client_name: str) -> str:
        is_lower = is_lower_course(client_name)

        code = BellService.get_schedule_code(weekday, is_lower)

        try:
            bell = Bell.objects.get(
                schedule_type__code=code,
                lesson_number=lesson_number
            )
            return bell.display_text
        except Bell.DoesNotExist:
            return "Нет времени"
