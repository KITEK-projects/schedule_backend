from schedule.redis import clear_all_cache
from .services import set_schedule
from django import forms
from django.shortcuts import render, redirect


def upload_and_parse_html(admin_instance):
    def view(request):
        if request.method == "POST":
            uploaded_file = request.FILES.get("html_file")
            send_notifications = request.POST.get("send_notifications") == "on"

            if not uploaded_file:
                admin_instance.message_user(request, "Файл не был загружен.", level="error")
                return redirect(".")

            if not uploaded_file.name.endswith(".html"):
                admin_instance.message_user(
                    request, "Файл должен иметь расширение .html", level="error"
                )
                return redirect(".")

            content_type = uploaded_file.content_type
            if content_type not in ("text/html", "application/octet-stream"):
                admin_instance.message_user(
                    request,
                    f"Неверный тип содержимого файла: {content_type}",
                    level="error",
                )
                return redirect(".")

            try:
                content = uploaded_file.read().decode("windows-1251", errors="replace")

                set_schedule(content, uploaded_file, send_notifications)

                admin_instance.message_user(
                    request,
                    "Расписание успешно загружено и сохранено.",
                    level="success",
                )

                clear_all_cache()

                if send_notifications:
                    admin_instance.message_user(
                        request, "📢 Уведомления отправлены.", level="info"
                    )

            except Exception as e:
                admin_instance.message_user(request, f"Ошибка: {str(e)}", level="error")
                return redirect(".")

        class UploadFileForm(forms.Form):
            html_file = forms.FileField(label="Выберите HTML файл")

        form = UploadFileForm()
        return render(request, "admin/add.html", {"form": form})

    return view
