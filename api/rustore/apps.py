import threading
from django.apps import AppConfig


class RustoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rustore'

    def ready(self):
        from rustore.background import start_background_tasks
        threading.Thread(target=start_background_tasks, daemon=True).start()

