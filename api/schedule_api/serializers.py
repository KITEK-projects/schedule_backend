from rest_framework import serializers
from .models import *

class ItemLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemLesson
        fields = ['title', 'type', 'partner', 'location']

class LessonSerializer(serializers.ModelSerializer):
    items = ItemLessonSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ['number', 'items']

class ScheduleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Schedule
        fields = ['date', 'lessons']

class ClientSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Client
        fields = ['client_name', 'is_teacher', 'schedules']
        
    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        
        client_name = validated_data.get('client_name')
        is_teacher = validated_data.get('is_teacher')
        client, created = Client.objects.get_or_create(client_name=client_name, is_teacher=is_teacher)

        for schedule_data in schedules_data:
            lessons_data = schedule_data.pop('lessons', [])
            schedule_date = schedule_data['date']
            
            schedule, _ = Schedule.objects.get_or_create(client=client, date=schedule_date)
            
            Lesson.objects.filter(schedule=schedule).delete()
            for lesson_data in lessons_data:
                items_data = lesson_data.pop('items', [])
                lesson_number = lesson_data['number']
                
                lesson, _ = Lesson.objects.get_or_create(schedule=schedule, number=lesson_number)
                
                ItemLesson.objects.filter(lesson=lesson).delete()
                for item_data in items_data:
                    item_lesson, created = ItemLesson.objects.get_or_create(lesson=lesson, **item_data)

        return client

        
    def destroy(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        
        # Fetch client using client_name
        client_name = validated_data.get("client_name")
        client = Client.objects.get(client_name=client_name)

        for schedule_data in schedules_data:
            schedule_date = schedule_data['date']
            
            # Fetch schedule using client and date
            schedule = Schedule.objects.get(client=client, date=schedule_date)

            for lesson_data in schedule_data.get('lessons', []):
                lesson_number = lesson_data['number']
                
                # Fetch lesson using schedule and lesson number
                lesson = Lesson.objects.get(schedule=schedule, number=lesson_number)

                # Delete items related to the lesson
                items_data = lesson_data.get('items', [])
                for item_data in items_data:
                    ItemLesson.objects.filter(lesson=lesson, **item_data).delete()

                # Check if there are any remaining ItemLessons; if not, delete the lesson
                if not ItemLesson.objects.filter(lesson=lesson).exists():
                    lesson.delete()

            # Check if there are any remaining Lessons; if not, delete the schedule
            if not Lesson.objects.filter(schedule=schedule).exists():
                schedule.delete()

        # Check if there are any remaining Schedules; if not, delete the client
        if not Schedule.objects.filter(client=client).exists():
            client.delete()

        return client




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'is_admin', 'name', 'is_super_admin']