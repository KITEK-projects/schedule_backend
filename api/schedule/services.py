from datetime import datetime, date
from typing import List
from schedule.models import Client, Lesson, ScheduleDay, ScheduleFile
from schedule.parsers import html_parse
from schedule.schemas import ClientSchema, LessonSchema


def get_schedule_for_client(client_name: str, client_time: date) -> ClientSchema:
    scheduleDays = ScheduleDay.objects.filter(client__client_name=client_name)

    data: ClientSchema = {
        "client_name": client_name,
        "schedules": [],
    }

    for scheduleDay in scheduleDays:
        if scheduleDay.date < client_time:
            # Пропускаем дни, которые раньше указанной даты
            continue

        date = scheduleDay.date.strftime("%Y-%m-%d")
        lessons: List[LessonSchema] = []

        for lesson in scheduleDay.lessons.all():
            # Ищем существующий урок с таким номером
            local_lesson = next(
                (obj for obj in lessons if obj.number == lesson.number), None
            )
            # Если урока нет - создаем новый и добавляем в список
            if local_lesson is None:
                local_lesson = LessonSchema(number=lesson.number, items=[])
                lessons.append(local_lesson)

            # Добавляем информацию об уроке
            local_lesson.items.append(
                {
                    "title": lesson.title,
                    "type": lesson.type,
                    "partner": lesson.partner,
                    "location": lesson.location or "",
                }
            )

        data["schedules"].append(
            {
                "date": date,
                "lessons": sorted(lessons, key=lambda x: x.number),
            }
        )

    if len(data["schedules"]) == 0:
        data["schedules"].append(
            {"date": client_time.strftime("%Y-%m-%d"), "lessons": []}
        )

    return data


def set_schedule(content, uploaded_file) -> None:
    parsed_data = html_parse(content)
    for item in parsed_data:
        client, _ = Client.objects.get_or_create(
            client_name=item["client_name"], is_teacher=item["is_teacher"]
        )
        for schedule in item["schedules"]:
            scheduleDay, _ = ScheduleDay.objects.get_or_create(
                date=datetime.fromisoformat(schedule["date"]).date(),
                client=client,
            )

            scheduleDay.lessons.all().delete()

            for lesson in schedule["lessons"]:
                Lesson.objects.create(
                    schedule=scheduleDay,
                    number=lesson["number"],
                    title=lesson["title"],
                    type=lesson["type"],
                    partner=lesson["partner"],
                    location=lesson["location"],
                )

    ScheduleFile.objects.create(
        file_name=uploaded_file.name,
        schedule_file=uploaded_file,
    )
