from django.urls import path
from unfold.admin import ModelAdmin
from unfold.sites import UnfoldAdminSite
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from schedule.views import upload_and_parse_html


class MyAdminSite(UnfoldAdminSite):
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

admin.site.unregister(User)
admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
