from django.contrib import admin
from .models import Client, ScheduleDay, Lesson, ScheduleFile, TimeOfBell
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Client, ScheduleDay, Lesson, ScheduleFile
from app.admin import admin_site


class ClientAdmin(admin.ModelAdmin):
    search_fields = ("client_name",)
    list_display = ("client_name", "is_teacher")
    list_filter = ("client_name", "is_teacher")


class ScheduleDayAdmin(admin.ModelAdmin):
    search_fields = ("client__client_name",)
    list_display = ("id", "client", "date")
    list_filter = ("date", "client")


class LessonAdmin(admin.ModelAdmin):
    search_fields = ("schedule__client__client_name", "title")
    list_display = ("schedule", "schedule__id", "schedule__client__client_name", "number", "title", "type", "partner", "location")
    list_filter = ("schedule", "number", "title", "type", "partner", "location")


class ScheduleFileAdmin(admin.ModelAdmin):
    list_display = ("file_name", "created_at", "schedule_file")
    list_filter = ("file_name", "created_at")


class TimeOfBellAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "use_curator_hour", "curator_hour")


admin_site.register(Client, ClientAdmin)
admin_site.register(ScheduleDay, ScheduleDayAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(ScheduleFile, ScheduleFileAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(TimeOfBell, TimeOfBellAdmin)
