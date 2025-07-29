from django.contrib import admin
from .models import Client, ScheduleDay, Lesson, ScheduleFile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Client, ScheduleDay, Lesson, ScheduleFile
from app.admin import admin_site


class ClientAdmin(admin.ModelAdmin):
    list_display = ("client_name", "is_teacher")
    list_filter = ("client_name", "is_teacher")


class ScheduleDayAdmin(admin.ModelAdmin):
    list_display = ("client", "date")
    list_filter = ("date", "client")


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
