from typing import List, Optional
from ninja import Schema


class ClientListSchema(Schema):
    groups: List[str]
    teachers: List[str]


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
    ascii_name: str
    last_update: str
    schedules: List[ScheduleDaySchema]
