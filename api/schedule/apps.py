from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
import os

class ScheduleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "schedule"

    def ready(self):
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__), '..', 'service-account.json')
            cred = credentials.Certificate(os.path.abspath(cred_path))
            firebase_admin.initialize_app(cred)
