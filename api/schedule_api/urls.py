from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('schedule/', views.ScheduleApiView.as_view()),
    path('clients/', views.ClientsApiView.as_view()),
    path('admin/', admin.site.urls)
]
