from typing import List, Optional
from ninja import Field, Schema


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
    time: str
    items: List[LessonItemSchema]


class ScheduleDaySchema(Schema):
    date: str
    weekday: int
    lessons: List[LessonSchema]


class ClientSchema(Schema):
    client_name: str
    last_update: str
    schedules: List[ScheduleDaySchema] = Field(default_factory=list)

