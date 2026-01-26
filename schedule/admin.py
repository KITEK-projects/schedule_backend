from django.contrib import admin
from .models import Client, ScheduleDay, Lesson, ScheduleFile, ScheduleTimeType, Bell
from app.admin import admin_site
from import_export.admin import ImportExportModelAdmin
from import_export import resources


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
    list_display = ("schedule", "schedule__id", "schedule__client__client_name", "number", "title", "type", "partner",
                    "location")
    list_filter = ("schedule", "number", "title", "type", "partner", "location")


class ScheduleFileAdmin(admin.ModelAdmin):
    list_display = ("file_name", "created_at", "schedule_file")
    list_filter = ("file_name", "created_at")


class BellInline(admin.TabularInline):
    model = Bell
    extra = 7
    max_num = 10
    fields = ('lesson_number', 'display_text')


class BellResource(resources.ModelResource):
    class Meta:
        model = Bell


class ScheduleTimeTypeAdmin(ImportExportModelAdmin):
    list_display = ("code", "name")
    list_filter = ("code", "name")
    inlines = [BellInline]


class BellAdmin(ImportExportModelAdmin):
    list_display = ('schedule_type', 'lesson_number', 'display_text')


admin_site.register(Client, ClientAdmin)
admin_site.register(ScheduleDay, ScheduleDayAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(ScheduleFile, ScheduleFileAdmin)
admin_site.register(ScheduleTimeType, ScheduleTimeTypeAdmin)
admin_site.register(Bell, BellAdmin)
