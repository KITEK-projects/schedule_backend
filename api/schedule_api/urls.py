from django.urls import path

from . import views

urlpatterns = [
    path('schedule/', views.ScheduleApiView.as_view()),
    path('clients/', views.ClientsApiView.as_view()),
    path('edit/', views.ScheduleEditApiView.as_view())
]
