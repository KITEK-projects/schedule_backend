from typing import List, Optional
from ninja import Schema
from .models import Client, Lesson, ScheduleDay


class LessonItemSchema(Schema):
    title: str
    type: str
    partner: str
    location: Optional[str] = None


class LessonSchema(Schema):
    number: int
    items: List[LessonItemSchema]


class ScheduleDaySchema(Schema):
    date: str
    lessons: List[LessonSchema]


class ClientSchema(Schema):
    client_name: str
    schedules: List[ScheduleDaySchema]
