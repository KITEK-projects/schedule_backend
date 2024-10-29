from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import date, timedelta

from .models import *
from .serializers import *


from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import clients, schedules

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
            try:
                is_teacher = bool(int(is_teacher))
            except ValueError:
                return Response({'error': 'Параметр is_teacher должен быть 0 или 1'}, status=status.HTTP_400_BAD_REQUEST)

            clients_list = clients.objects.filter(is_teacher=is_teacher)
        else:
            return Response({'error': 'Обязательный параметр is_teacher не передан'}, status=status.HTTP_400_BAD_REQUEST)

        client_data = [client.client_name for client in clients_list]

        return Response(client_data, status=status.HTTP_200_OK)