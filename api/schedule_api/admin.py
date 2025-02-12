from django.contrib import admin
from django.shortcuts import redirect, render
from schedule_api.models import *
from .parsers import html_parse
from django.http import HttpResponse

from django.urls import path


class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'is_teacher')
    list_filter = ('client_name', 'is_teacher')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-html/', self.admin_site.admin_view(self.upload_and_parse_html), name='upload_html'),
        ]
        return custom_urls + urls

    def upload_and_parse_html(self, request):
        if request.method == 'POST':
            uploaded_file = request.FILES.get('html_file')
            if not uploaded_file:
                self.message_user(request, "Файл не был загружен.", level='error')
                return redirect('.')

            try:
                html_content = uploaded_file.read().decode('windows-1251')
                parsed_data = html_parse(html_content)

                for entry in parsed_data:
                    client_name = entry['client_name']
                    is_teacher = entry['is_teacher']
                    schedules = entry['schedules']

                    client, _ = Client.objects.get_or_create(
                        client_name=client_name,
                        defaults={'is_teacher': is_teacher}
                    )

                    for schedule in schedules:
                        schedule_date = schedule['date']
                        lessons = schedule['lessons']

                        schedule_obj, _ = Schedule.objects.get_or_create(
                            client=client,
                            date=schedule_date
                        )

                        for lesson in lessons:
                            lesson_number = lesson['number']
                            items = lesson['items']

                            lesson_obj, _ = Lesson.objects.get_or_create(
                                schedule=schedule_obj,
                                number=lesson_number
                            )

                            for item in items:
                                ItemLesson.objects.get_or_create(
                                    lesson=lesson_obj,
                                    title=item['title'],
                                    type=item['type'],
                                    partner=item['partner'],
                                    location=item['location']
                                )

                self.message_user(request, "Данные успешно загружены и сохранены.")
            except Exception as e:
                self.message_user(request, f"Ошибка при обработке файла: {str(e)}", level='error')

        from django import forms
        class UploadFileForm(forms.Form):
            html_file = forms.FileField(label="Выберите HTML файл")

        form = UploadFileForm()
        return render(request, 'admin/upload.html', {'form': form})
    

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
