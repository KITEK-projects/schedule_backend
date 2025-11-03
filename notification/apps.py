import os

import firebase_admin
from django.apps import AppConfig
from firebase_admin import credentials


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__), '..', 'service-account.json')
            cred = credentials.Certificate(os.path.abspath(cred_path))
            firebase_admin.initialize_app(cred)
