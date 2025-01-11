from rest_framework import serializers
from .models import *

class ItemLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemLesson
        fields = ['title', "type", "partner", "location"]

class LessonSerializer(serializers.ModelSerializer):
    item_lesson = ItemLessonSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ['number', "item_lesson"]

class SchedulesSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(many=True)

    class Meta:
        model = Schedule
        fields = ['date', 'classes']


class ClientsSerializer(serializers.ModelSerializer):
    schedule = SchedulesSerializer(many=True, source='schedules')  # Используем related_name 'schedules'

    class Meta:
        model = Client
        fields = ['client_name', 'is_teacher', 'schedule']


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_id', 'is_admin', 'name', 'is_super_admin']