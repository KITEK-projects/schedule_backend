from django.contrib import admin, messages
from django.urls import path

from admin_interface.models import Theme
from admin_interface.admin import ThemeAdmin

from schedule.views import upload_and_parse_html


class MyAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add/",
                self.admin_view(upload_and_parse_html(self)),
                name="add",
            ),
        ]
        return custom_urls + urls

    def message_user(
        self, request, message, level="info", extra_tags="", fail_silently=False
    ):
        """
        Send a message to the user. Default level is 'info'.
        """

        levels = {
            "info": messages.INFO,
            "success": messages.SUCCESS,
            "warning": messages.WARNING,
            "error": messages.ERROR,
        }
        level = levels.get(level, messages.INFO)
        messages.add_message(
            request, level, message, extra_tags=extra_tags, fail_silently=fail_silently
        )


admin_site = MyAdminSite()

try:
    admin_site.register(Theme, ThemeAdmin)
except:
    pass