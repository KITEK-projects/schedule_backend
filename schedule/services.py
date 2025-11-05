from datetime import datetime, date, timedelta
from typing import List
from django.db import transaction
from django.utils.timezone import localtime
from schedule.models import Client, Lesson, ScheduleDay, ScheduleFile, TimeOfBell
from schedule.parsers import html_parse
from schedule.schemas import (
    ClientSchema,
    LessonItemSchema,
    LessonSchema,
    ScheduleDaySchema,
)
from notification.notification import send_notifications_by_clients
from ninja.errors import HttpError
from unidecode import unidecode

from schedule.urls import course_flag, format_lesson


def get_schedule_for_client(client_name: str, client_time: date) -> ClientSchema:
    schedule_bells = ScheduleBells()
    scheduleDays: List[ScheduleDay] = ScheduleDay.objects.filter(
        client__client_name=client_name
    )
    client = Client.objects.filter(client_name=client_name).first()

    if client is None:
        raise HttpError(404, "Client not found")

    last_update_local = localtime(client.last_update).isoformat()

    data = ClientSchema(
        client_name=client.client_name,
        ascii_name=client.ascii_name,
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
                    time=schedule_bells.get_bell(
                        number=lesson.number,
                        week_day=week_day,
                        client=(
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


class ScheduleBells:
    def __init__(self):
        self.params = TimeOfBell.objects.last()
        if not self.params:
            self.bells = [["Параметры не найдены"]] * 6
            self.bells_on_monday = [["Параметры не найдены"]] * 6
            self.bells_on_saturday = [["Параметры не найдены"]] * 6
            return
        self.bells = [
            self._generate_schedule_bells(is_lower=True),
            self._generate_schedule_bells(),
        ]
        self.bells_on_monday = [
            self._generate_schedule_bells(is_lower=True, is_monday=True),
            self._generate_schedule_bells(is_monday=True),
        ]
        self.bells_on_saturday = [
            self._generate_schedule_bells(is_lower=True, is_saturday=True),
            self._generate_schedule_bells(is_saturday=True),
        ]

    def get_bell(self, number: int, week_day: int, client: str):
        flag = course_flag(client)
        if week_day == 0 and self.params.use_curator_hour:
            return self.bells_on_monday[flag][number - 1]
        elif week_day == 5:
            return self.bells_on_saturday[flag][number - 1]
        else:
            return self.bells[flag][number - 1]

    def _generate_schedule_bells(
        self, is_lower: bool = False, is_monday: bool = False, is_saturday: bool = False
    ) -> List[str]:
        p = self.params
        curator = timedelta(minutes=p.curator_hour if is_monday else 0)

        if is_monday:
            lesson = timedelta(minutes=p.lesson)
            lunch_break = timedelta(minutes=p.lunch_break_monday)
        elif is_saturday:
            lesson = timedelta(minutes=p.lesson_saturday)
            lunch_break = timedelta(minutes=p.lunch_break_saturday)
        else:
            lesson = timedelta(minutes=p.lesson)
            lunch_break = timedelta(minutes=p.lunch_break)

        start = p.get_start_timedelta()
        end = start + lesson
        result = [format_lesson(start, end)]

        if is_lower:
            if is_saturday:
                first_half = timedelta(minutes=p.first_half)
                second_half = timedelta(minutes=p.second_half)
            else:
                first_half = lesson / 2
                second_half = lesson / 2


            start = end + timedelta(minutes=p.break_after_1) + curator
            end = start + first_half
            part1 = format_lesson(start, end)

            start = end + lunch_break
            end = start + second_half
            part2 = format_lesson(start, end)

            result.append(f"{part1}, {part2}")
        else:
            start = end + timedelta(minutes=p.break_after_1) + curator
            end = start + lesson
            result.append(format_lesson(start, end))
            end += lunch_break

        last_end = end + timedelta(minutes=p.break_after_2)

        for i in range(3, 7):
            start, end = last_end, last_end + lesson
            result.append(format_lesson(start, end))
            last_end = end + timedelta(minutes=getattr(p, f"break_after_{i}", 0))

        return result
