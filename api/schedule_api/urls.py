from django.urls import path
from schedule_api.admin import admin_site

from . import views

urlpatterns = [
    path("schedule/", views.ScheduleApiView.as_view()),
    path("clients/", views.ClientsApiView.as_view()),
    path("admin/", admin_site.urls),
]
