from django.core.management.base import BaseCommand
from schedule_api.models import users

class Command(BaseCommand):
    help = 'Инициализация базовых пользователей'

    def handle(self, *args, **kwargs):
        # Список ID пользователей, которые должны быть в системе
        default_users = [
            {'user_id': '1509968545', 'is_admin': True, 'name': 'I', 'is_super_admin': True},
            {'user_id': '267587484', 'is_admin': True, 'name': 'Павел Алексеевич', 'is_super_admin': True},
        ]

        for user_data in default_users:
            user, created = users.objects.get_or_create(
                user_id=user_data['user_id'],
                name=user_data['name'],
                defaults={'is_admin': user_data['is_admin'], 'is_super_admin': user_data['is_super_admin']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан пользователь с ID: {user.user_id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Пользователь с ID: {user.user_id} уже существует')
                )
