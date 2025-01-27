from django.utils.dateparse import parse_datetime

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics

from .models import *
from .serializers import *
from .decorators import internal_api


BOT = 'schedule-bot'


# class ScheduleApiView(generics.ListAPIView):
#     queryset = Client.objects.all()
#     serializer_class = UsersSerializer
    
class ScheduleApiView(mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    
    def get(self, request, *args, **kwargs):
        client_name = request.GET.get('client_name')
        x_client_time = request.headers.get('x-client-time')

        queryset = self.queryset
        
        if client_name and x_client_time:
            try:
                queryset = queryset.get(client_name=client_name)
                client_time = parse_datetime(x_client_time)

                if client_time is None:
                    return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
                
                date_to_filter = client_time.date()
                filtered_schedules = queryset.schedules.filter(date__gte=date_to_filter)

                # Serialize the filtered schedules
                schedule_serializer = ScheduleSerializer(filtered_schedules, many=True)

                # Prepare the response data
                response_data = {
                    "client_name": queryset.client_name,
                    'is_teacher': queryset.is_teacher,
                    "schedules": schedule_serializer.data
                }
                
                if response_data['schedules'] == []:
                    return Response({"detail": "У вас нет расписания"}, status=status.HTTP_404_NOT_FOUND)

                return Response(response_data, status=status.HTTP_200_OK)
            
            except Client.DoesNotExist:
                return Response({'detail': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if not client_name:
                return Response({'detail': 'Нужен client_name(query)'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Нужен x-client-time(header)'}, status=status.HTTP_400_BAD_REQUEST)
    
    @internal_api
    def post(self, request, *args, **kwargs):
        data = request.data
        
        serializer = self.get_serializer(data=data, many=True)
        if serializer.is_valid():
            clients = serializer.save()
            return Response(self.get_serializer(clients, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @internal_api
    def delete(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        
        if serializer.is_valid():
            for item in serializer.validated_data:
                client_name = item.get('client_name')
                schedules_data = item.get('schedules', [])
                
                try:
                    client = Client.objects.get(client_name=client_name)
                    for schedule_data in schedules_data:
                        schedule_date = schedule_data['date']
                        try:
                            schedule = Schedule.objects.get(client=client, date=schedule_date)
                            schedule.delete()
                        except Schedule.DoesNotExist:
                            continue 

                    if not Schedule.objects.filter(client=client).exists():
                        client.delete()    
                except Exception:
                    continue

            return Response({'message': 'Удаление выполнено!'}, status=status.HTTP_202_ACCEPTED)
        else:
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
            
        
class UsersApiView(APIView):
    @internal_api
    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(User, user_id=user_id)
            if user.is_admin:
                return Response({'is_admin': True, "is_super_admin": user.is_super_admin}, status=status.HTTP_200_OK)
            return Response({'is_admin': False, "is_super_admin": user.is_super_admin}, status=status.HTTP_200_OK)
        
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
        
        

