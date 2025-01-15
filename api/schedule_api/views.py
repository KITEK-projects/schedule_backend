import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from rest_framework.views import APIView
from rest_framework import status
from .models import Client, Schedule, User
from rest_framework.generics import get_object_or_404
from .serializers import UserSerializer

from .models import *
from .serializers import *
from .decorators import internal_api

from rest_framework import generics
from rest_framework import mixins

BOT = 'schedule-bot'


# class ScheduleApiView(generics.ListAPIView):
#     queryset = Client.objects.all()
#     serializer_class = UsersSerializer
    
class ScheduleApiView(mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def delete(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            client = serializer.destroy(serializer.validated_data)
            return Response({'message': 'Удаление выполнено!'}, status=status.HTTP_204_NO_CONTENT)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientsApiView(APIView):
    def get(self, request):
        is_teacher = request.query_params.get('is_teacher', None)

        if is_teacher is not None:
            if is_teacher.lower() == 'true':
                is_teacher = True
            elif is_teacher.lower() == 'false':
                is_teacher = False
            else:
                return Response({'error': 'Параметр is_teacher должен быть true или false'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            clients_list = Client.objects.filter(is_teacher=is_teacher)
            
            if not clients_list.exists():
                return Response({'error': 'База данных пуста'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'error': 'Обязательный параметр is_teacher не передан'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        client_data = [client.client_name for client in clients_list]

        return Response(client_data, status=status.HTTP_200_OK)
    
    
class ScheduleEditApiView(APIView):
    @internal_api
    def put(self, request):
        try:
            schedule_data = request.data
            
            for client_data in schedule_data:
                client_name = client_data.get("client")
                is_teacher = client_data.get("is_teacher", False)

                client, _ = Client.objects.get_or_create(
                    client_name=client_name,
                    is_teacher=is_teacher
                )

                # Обрабатываем каждое расписание
                for schedule_item in client_data.get("schedule", []):
                    date = schedule_item.get("date")
                    classes_data = schedule_item.get("classes", [])

                    # Проверяем, существует ли расписание
                    existing_schedule, _ = Schedule.objects.get_or_create(client=client, date=date)

                    # Создаем или обновляем уроки
                    for class_data in classes_data:
                        # Создаем или обновляем объект Lesson
                        lesson, _ = Lesson.objects.get_or_create(
                            schedule=existing_schedule,
                            number=class_data["number"]
                        )
                        # Обновляем или создаем ItemLesson
                        item_res, _ = ItemLesson.objects.update_or_create(
                            schedule=lesson,
                            title=class_data["title"],
                            defaults={
                                'type': class_data.get("type"),
                                'partner': class_data.get("partner"),
                                'location': class_data.get("location"),
                            },
                        )
                
            return Response({"detail": "Schedules updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @internal_api
    def delete(self, request):
        try:
            schedule_data = request.data
            for client_data in schedule_data:
                # Получаем одного клиента расписания
                client_name = client_data.get("client")
                is_teacher = client_data.get("is_teacher", False)

                # Находим такого в бд
                client, _ = Client.objects.get_or_create(
                    client_name=client_name,
                    is_teacher=is_teacher
                )

                # Получаем расписания клиента
                existing_schedules = Schedule.objects.filter(client=client)

                # Перебераем входной json
                for schedule_item in client_data.get("schedule", []):
                    # Получаем дату из каждого айтема
                    date = schedule_item.get("date")
                    existing_schedules.filter(date=date).delete()

                # Проверяем есть ли у клиента другие расписания
                if not existing_schedules.exists():
                    client.delete()

            return Response({"detail": "Schedules and empty clients deleted successfully."}, 
                          status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class UsersApiView(APIView):
    @internal_api
    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(User, user_id=user_id)
            if user.is_admin:
                return Response({'is_admin': True, "is_super_admin": user.is_super_admin}, status=status.HTTP_200_OK)
            return Response({'is_admin': False, "is_super_admin": user.is_super_admin}, status=status.HTTP_200_OK)
        
        # Если user_id не передан, возвращаем список всех пользователей
        all_users = User.objects.all()
        serializer = UserSerializer(all_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @internal_api
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @internal_api
    def put(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @internal_api
    def delete(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        

