from rest_framework import serializers
from .models import *


class ItemLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemLesson
        fields = ["title", "type", "partner", "location"]


class LessonSerializer(serializers.ModelSerializer):
    items = ItemLessonSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ["number", "items"]


class ScheduleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Schedule
        fields = ["date", "lessons"]


class ClientSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Client
        fields = ["client_name", "is_teacher", "schedules"]

    def create(self, validated_data):
        return self.update_or_create_client(validated_data)

    def update(self, instance, validated_data):
        return self.update_or_create_client(validated_data)

    def update_or_create_client(self, validated_data):
        schedules_data = validated_data.pop("schedules", [])
        client_name = validated_data.get("client_name")
        is_teacher = validated_data.get("is_teacher")

        client, _ = Client.objects.get_or_create(
            client_name=client_name, defaults={"is_teacher": is_teacher}
        )

        if client.is_teacher != is_teacher:
            client.is_teacher = is_teacher
            client.save()

        for schedule_data in schedules_data:
            date = schedule_data["date"]
            lessons_data = schedule_data.get("lessons", [])

            schedule, _ = Schedule.objects.get_or_create(client=client, date=date)

            existing_lessons = {
                lesson.number: lesson for lesson in schedule.lessons.all()
            }
            incoming_numbers = set()

            for lesson_data in lessons_data:
                number = lesson_data["number"]
                items_data = lesson_data.get("items", [])
                incoming_numbers.add(number)

                lesson = existing_lessons.get(number)
                if not lesson:
                    lesson = Lesson.objects.create(schedule=schedule, number=number)
                else:
                    lesson.items.all().delete()

                for item_data in items_data:
                    ItemLesson.objects.create(lesson=lesson, **item_data)

            for number, lesson in existing_lessons.items():
                if number not in incoming_numbers:
                    lesson.delete()

        return client
