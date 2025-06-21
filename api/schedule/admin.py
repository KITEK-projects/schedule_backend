from django.contrib import admin, messages
from django.shortcuts import redirect, render
from .models import *
from .services import set_schedule
from django.urls import path
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render, redirect
from .notification import send_notification
from .models import Client, ScheduleDay, Lesson, ScheduleFile
from django import forms
from datetime import datetime


class MyAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add/",
                self.admin_view(self.upload_and_parse_html),
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

    def upload_and_parse_html(self, request):
        if request.method == "POST":
            uploaded_file = request.FILES.get("html_file")
            send_notifications = request.POST.get("send_notifications") == "on"

            if not uploaded_file:
                self.message_user(request, "Файл не был загружен.", level="error")
                return redirect(".")

            if not uploaded_file.name.endswith(".html"):
                self.message_user(
                    request, "Файл должен иметь расширение .html", level="error"
                )
                return redirect(".")

            content_type = uploaded_file.content_type
            if content_type not in ("text/html", "application/octet-stream"):
                self.message_user(
                    request,
                    f"Неверный тип содержимого файла: {content_type}",
                    level="error",
                )
                return redirect(".")

            try:
                content = uploaded_file.read().decode("windows-1251", errors="replace")
                set_schedule(content, uploaded_file)

                self.message_user(
                    request,
                    "Расписание успешно загружено и сохранено.",
                    level="success",
                )

                if send_notifications:
                    send_notification()
                    self.message_user(
                        request, "📢 Уведомления отправлены.", level="info"
                    )

            except Exception as e:
                self.message_user(request, f"Ошибка: {str(e)}", level="error")
                return redirect(".")

        # Форма для GET-запроса
        class UploadFileForm(forms.Form):
            html_file = forms.FileField(label="Выберите HTML файл")

        form = UploadFileForm()
        return render(request, "admin/add.html", {"form": form})


admin_site = MyAdminSite()


class ClientAdmin(admin.ModelAdmin):
    list_display = ("client_name", "is_teacher")
    list_filter = ("client_name", "is_teacher")


class ScheduleDayAdmin(admin.ModelAdmin):
    list_display = ("client_name", "date")
    list_filter = ("date", "client")

    def client_name(self, obj):
        return obj.client.client_name

    client_name.short_description = "Клиент"
    client_name.admin_order_field = "client__client_name"


class LessonAdmin(admin.ModelAdmin):
    list_display = ("schedule", "number", "title", "type", "partner", "location")
    list_filter = ("schedule", "number", "title", "type", "partner", "location")


class ScheduleFileAdmin(admin.ModelAdmin):
    list_display = ("file_name", "created_at", "schedule_file")
    list_filter = ("file_name", "created_at")


admin_site.register(Client, ClientAdmin)
admin_site.register(ScheduleDay, ScheduleDayAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(ScheduleFile, ScheduleFileAdmin)
admin_site.register(User, UserAdmin)
