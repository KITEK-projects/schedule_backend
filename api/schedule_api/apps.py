from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command

def init_users(sender, **kwargs):
    call_command('init_users')

class ScheduleApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedule_api'

    def ready(self):
        post_migrate.connect(init_users, sender=self)
