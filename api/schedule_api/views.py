import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from rest_framework.views import APIView
from rest_framework import status
from .models import clients, schedules, Users
from rest_framework.generics import get_object_or_404
from .serializers import UsersSerializer

from .models import *
from .serializers import *
from .decorators import internal_api

BOT = 'schedule-bot'


class ScheduleApiView(APIView):
    def get(self, request):
        client_name = request.query_params.get('client', None)
        
        # Извлекаем дату из заголовков
        request_date_str = request.headers.get('X-CLIENT-TIME', None)  # Формат 2024-10-23T12:50:16.999Z
        
        if request_date_str:
            try:
                # Пытается парсить дату из стринга
                request_date = datetime.fromisoformat(request_date_str).date()
            except:
                # В случае ощибки берет дату сервера
                request_date =datetime.today().date()
        else:
            # Если дата не указана, используем дату сервера
            request_date = datetime.today().date()
        
        try:
            # Находим клиента по имени
            client = clients.objects.get(client_name=client_name)
            
            # Получаем расписания клиента начиная с даты из запроса
            schedules_list = schedules.objects.filter(client=client, date__gte=request_date)
            
            if schedules_list.exists():
                # Если есть расписания, сериализуем их
                data = {
                    'client': client.client_name,
                    'schedule': []
                }
                for schedule in schedules_list:
                    # Для каждого расписания добавляем информацию о классах
                    classes_list = schedule.classes.all()
                    data['schedule'].append({
                        'date': schedule.date,
                        'classes': [{
                            'number': c.number,
                            'title': c.title,
                            'type': c.type,
                            'partner': c.partner,
                            'location': c.location,
                        } for c in classes_list]
                    })
                
                return Response(data)
            else:
                return Response({'error': "У вас нет расписания"}, status=status.HTTP_404_NOT_FOUND)
        
        except clients.DoesNotExist:
            return Response({'error': "Клиент не найден"}, status=status.HTTP_400_BAD_REQUEST)


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

            clients_list = clients.objects.filter(is_teacher=is_teacher)
            
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

                client, _ = clients.objects.get_or_create(
                    client_name=client_name,
                    is_teacher=is_teacher
                )

                # Обрабатываем каждое расписание
                for schedule_item in client_data.get("schedule", []):
                    date = schedule_item.get("date")
                    classes_data = schedule_item.get("classes", [])

                    # Проверяем, существует ли расписание перед удалением
                    existing_schedule = schedules.objects.filter(client=client, date=date)
                    if existing_schedule.exists():
                        existing_schedule.delete()

                    # Создаем новое расписание
                    schedule = schedules.objects.create(
                        client=client,
                        date=date
                    )

                    # Создаем новые классы для расписания
                    for class_data in classes_data:
                        classes.objects.create(
                            schedule=schedule,
                            **class_data
                        )

            return Response({"detail": "Schedules updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @internal_api
    def delete(self, request):
        try:
            schedule_data = request.data
            for client_data in schedule_data:
                client_name = client_data.get("client")
                is_teacher = client_data.get("is_teacher", False)

                client, _ = clients.objects.get_or_create(
                    client_name=client_name,
                    is_teacher=is_teacher
                )

                # Удаляем расписания клиента
                schedules.objects.filter(client=client).delete()
                
                # Проверяем есть ли у клиента другие расписания
                if not schedules.objects.filter(client=client).exists():
                    # Если расписаний нет - удаляем клиента
                    client.delete()

            return Response({"detail": "Schedules and empty clients deleted successfully."}, 
                          status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class UsersApiView(APIView):
    @internal_api
    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(Users, user_id=user_id)
            if user.is_admin:
                return Response({'is_admin': True, "is_super_admin": user.is_super_admin}, status=status.HTTP_200_OK)
            return Response({'is_admin': False, "is_super_admin": user.is_super_admin}, status=status.HTTP_200_OK)
        
        # Если user_id не передан, возвращаем список всех пользователей
        all_users = Users.objects.all()
        serializer = UsersSerializer(all_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @internal_api
    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @internal_api
    def put(self, request, user_id):
        user = get_object_or_404(Users, user_id=user_id)
        serializer = UsersSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @internal_api
    def delete(self, request, user_id):
        user = get_object_or_404(Users, user_id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        

