from django.contrib import admin, messages
from django.shortcuts import redirect, render
from schedule_api.models import *
from .parsers import html_parse
from .serializers import ClientSerializer
from django.urls import path
from .notification import send_notification
from django import forms


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

            try:
                html_content = uploaded_file.read().decode("windows-1251")
                parsed_data = html_parse(html_content)

                serializer = ClientSerializer(data=parsed_data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    ScheduleFile.objects.create(
                        file_name=uploaded_file.name, schedule_file=uploaded_file
                    )

                self.message_user(request, "Данные успешно загружены и сохранены.")

                if send_notifications:
                    print("[ NOTIFICATION ] " + str(send_notification()))

            except Exception as e:
                self.message_user(
                    request, f"Ошибка при обработке файла: {str(e)}", level="error"
                )

        class UploadFileForm(forms.Form):
            html_file = forms.FileField(label="Выберите HTML файл")

        form = UploadFileForm()
        return render(request, "admin/add.html", {"form": form})


# Заменяем стандартный admin.site на наш кастомный
admin_site = MyAdminSite()


# Затем регистрируем все модели через наш кастомный admin_site
class ClientAdmin(admin.ModelAdmin):
    list_display = ("client_name", "is_teacher")
    list_filter = ("client_name", "is_teacher")


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("client", "date")
    list_filter = ("date",)


class LessonAdmin(admin.ModelAdmin):
    list_display = ("schedule", "number")
    list_filter = ("schedule", "number")


class ItemLessonAdmin(admin.ModelAdmin):
    list_display = ("lesson", "title", "type", "partner", "location")
    list_filter = ("title", "type", "partner", "location")


class ScheduleFileAdmin(admin.ModelAdmin):
    list_display = ("file_name", "date", "schedule_file")
    list_filter = ("file_name", "date")


admin_site.register(Client, ClientAdmin)
admin_site.register(Schedule, ScheduleAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(ItemLesson, ItemLessonAdmin)
admin_site.register(ScheduleFile, ScheduleFileAdmin)
