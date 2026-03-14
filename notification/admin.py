from django.contrib import admin, messages

from app.admin import admin_site
from notification.models import FCMToken
from notification.notification import send_notifications_by_clients
from schedule.models import Client
from unfold.admin import ModelAdmin

class FCMTokenAdmin(ModelAdmin):
    search_fields = ("client__client_name",)
    list_filter = ("client__client_name",)
    list_display = ("token", "client__client_name", "created_at", "last_used_at")
    actions = ["send_push_notification"]

    @admin.action(description="📨 Отправить уведомление выбранным токенам")
    def send_push_notification(self, request, queryset):
        """
        Отправить уведомление только тем клиентам, чьи токены выбраны в админке.
        """
        try:
            # Получаем всех клиентов, у которых есть выбранные токены
            client_ids = queryset.values_list("client_id", flat=True).distinct()
            clients = (
                Client.objects.filter(id__in=client_ids)
                .prefetch_related("fcm_tokens")
            )

            send_notifications_by_clients(clients)

            self.message_user(
                request,
                f"✅ Уведомления отправлены {clients.count()} клиентам.",
                level=messages.SUCCESS,
            )

        except Exception as e:
            self.message_user(
                request,
                f"🔥 Ошибка при отправке уведомлений: {e}",
                level=messages.ERROR,
            )

admin_site.register(FCMToken, FCMTokenAdmin)