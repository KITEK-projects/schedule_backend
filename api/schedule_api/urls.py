from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('schedule/', views.ScheduleApiView.as_view()),
    path('clients/', views.ClientsApiView.as_view()),
    path('users/', views.UsersApiView.as_view(), name='users-create'),
    path('users/<str:user_id>/', views.UsersApiView.as_view(), name='users-detail'),
    path('admin/', admin.site.urls)
]
