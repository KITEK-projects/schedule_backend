from datetime import datetime, date, timedelta
from typing import List
from schedule.models import Client, Lesson, ScheduleDay, ScheduleFile, TimeOfBell
from schedule.parsers import html_parse
from schedule.schemas import (
    ClientSchema,
    LessonItemSchema,
    LessonSchema,
    ScheduleDaySchema,
)
from schedule.notification import send_notifications
from schedule.helpers import make_topic_name
from ninja.errors import HttpError

from schedule.urls import course_flag, format_lesson


def get_schedule_for_client(client_name: str, client_time: date) -> ClientSchema:
    schedule_bells = ScheduleBells()
    scheduleDays: List[ScheduleDay] = ScheduleDay.objects.filter(
        client__client_name=client_name
    )
    client = Client.objects.filter(client_name=client_name).first()

    if client is None:
        raise HttpError(404, "Client not found")

    data = ClientSchema(
        client_name=client.client_name,
        last_update=client.last_update.strftime("%d.%m.%y, %H:%M"),
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
                        use_curator=True if week_day == 0 else False,
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
            ScheduleDaySchema(date=client_time.strftime("%Y-%m-%d"), week_day=client_time.weekday(), lessons=[])
        )

    return data


def set_schedule(content, uploaded_file, is_send_notifications: bool):
    clients = []
    parsed_data = html_parse(content)
    for item in parsed_data:
        client, _ = Client.objects.get_or_create(
            client_name=item["client_name"],
            is_teacher=item["is_teacher"],
            ascii_name=make_topic_name(item["client_name"]),
        )
        clients.append(client)
        for schedule in item["schedules"]:
            scheduleDay, _ = ScheduleDay.objects.get_or_create(
                date=datetime.fromisoformat(schedule["date"]).date(),
                client=client,
            )

            scheduleDay.lessons.all().delete()  # type: ignore

            lesson_to_create = []
            for lesson in schedule["lessons"]:
                lesson_to_create.append(
                    Lesson(
                        schedule=scheduleDay,
                        number=lesson["number"],
                        title=lesson["title"],
                        type=lesson["type"],
                        partner=lesson["partner"],
                        location=lesson.get("location", ""),
                    )
                )
            Lesson.objects.bulk_create(lesson_to_create)

        client.update_last_modified()

    if is_send_notifications:
        send_notifications(clients)

    ScheduleFile.objects.create(
        file_name=uploaded_file.name,
        schedule_file=uploaded_file,
    )


class ScheduleBells:
    def __init__(self):
        self.params = TimeOfBell.objects.last()
        if not self.params:
            self.lessons = ["Параметры не найдены"] * 6
            return
        self.bells = [
            self._generate_schedule_bells(True, False),
            self._generate_schedule_bells(False, False),
        ]
        self.bells_with_curator = [
            self._generate_schedule_bells(True, True),
            self._generate_schedule_bells(False, True),
        ]

    def get_bell(self, number: int, use_curator: bool, client: str):
        flag = course_flag(client)
        if use_curator and self.params.use_curator_hour:
            return self.bells_with_curator[flag][number - 1]
        else:
            return self.bells[flag][number - 1]

    def _generate_schedule_bells(
        self, is_lower: bool = False, use_curator_hour: bool = False
    ) -> List[str]:
        p = self.params
        lesson = timedelta(minutes=p.lesson)
        lunch_break = timedelta(minutes=p.lunch_break)
        curator = timedelta(minutes=p.curator_hour if use_curator_hour else 0)
        curator_offset = timedelta(
            minutes=p.lunch_break_offset if use_curator_hour else 0
        )

        start = p.get_start_timedelta()
        end = start + lesson
        result = [format_lesson(start, end)]

        if is_lower:
            half = lesson / 2
            start = end + timedelta(minutes=p.break_after_1) + curator
            end = start + half
            part1 = format_lesson(start, end)

            start = end + lunch_break + curator_offset
            end = start + half
            part2 = format_lesson(start, end)

            result.append(f"{part1}, {part2}")
        else:
            start = end + timedelta(minutes=p.break_after_1) + curator
            end = start + lesson
            result.append(format_lesson(start, end))
            end += lunch_break + curator_offset

        last_end = end + timedelta(minutes=p.break_after_2)

        for i in range(3, 7):
            start, end = last_end, last_end + lesson
            result.append(format_lesson(start, end))
            last_end = end + timedelta(minutes=getattr(p, f"break_after_{i}", 0))

        return result
