from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
import os

class ScheduleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "schedule"
