from rest_framework import serializers
from .models import *

class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = classes
        fields = ['number', 'title', 'type', 'partner', 'location']


class SchedulesSerializer(serializers.ModelSerializer):
    classes = ClassesSerializer(many=True)  # Используем related_name 'classes'

    class Meta:
        model = schedules
        fields = ['date', 'classes']


class ClientsSerializer(serializers.ModelSerializer):
    schedule = SchedulesSerializer(many=True, source='schedules')  # Используем related_name 'schedules'

    class Meta:
        model = clients
        fields = ['client_name', 'is_teacher', 'schedule']


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_id', 'is_admin', 'name', 'is_super_admin']