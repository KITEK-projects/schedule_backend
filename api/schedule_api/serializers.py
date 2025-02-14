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
        client, _ = Client.objects.get_or_create(
            client_name=client_name, 
            is_teacher=is_teacher
        )

        for schedule_data in schedules_data:
            lessons_data = schedule_data.pop('lessons', [])
            schedule_date = schedule_data.pop('date')
            
            schedule, _ = Schedule.objects.update_or_create(
                client=client,
                date=schedule_date,
                defaults=schedule_data
            )
            
            Lesson.objects.filter(schedule=schedule).delete()
            
            for lesson_data in lessons_data:
                items_data = lesson_data.pop('items', [])
                lesson_number = lesson_data.get('number')
                
                lesson = Lesson.objects.create(
                    schedule=schedule,
                    **lesson_data
                )
                
                ItemLesson.objects.filter(lesson=lesson).delete()
                for item_data in items_data:
                    ItemLesson.objects.create(lesson=lesson, **item_data)

        return client



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'is_admin', 'name', 'is_super_admin']