from django.contrib import admin
from schedule_api.models import *

class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'is_teacher')
    list_filter = ('client_name', 'is_teacher')
    
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('client', 'date')
    list_filter = ('date',)
    

class LessonAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'number')
    list_filter = ('schedule', 'number')
        

class ItemLessonAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'title', 'type', 'partner', 'location')
    list_filter = ('title', 'type', 'partner', 'location')


admin.site.register(Client, ClientAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(ItemLesson, ItemLessonAdmin)
admin.site.register(User)
