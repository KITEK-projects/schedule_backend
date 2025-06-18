from django.urls import path

from schedule_api.api import api

from schedule_api.admin import admin_site

urlpatterns = [
    path("", api.urls),
    path("admin/", admin_site.urls),
]
