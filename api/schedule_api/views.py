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
    
class ScheduleApiView(mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    
    def get(self, request, *args, **kwargs):
        client_name = request.GET.get('client_name')

        queryset = self.queryset
        
        if client_name:
            try:
                queryset = queryset.get(client_name=client_name)
            except Client.DoesNotExist:
                return Response({'detail': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Нужен client_name'}, status=status.HTTP_400_BAD_REQUEST)
                
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @internal_api
    def post(self, request, *args, **kwargs):
        data = request.data
        
        # Если данные - это список
        if isinstance(data, list):
            # Сериализуем данные
            serializer = self.get_serializer(data=data, many=True)
            if serializer.is_valid():
                # Сохраняем все объекты
                clients = serializer.save()
                return Response(self.get_serializer(clients, many=True).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Если данные - это один объект
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            client = serializer.save()
            return Response(self.get_serializer(client).data, status=status.HTTP_201_CREATED)

    
    @internal_api
    def delete(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.destroy(serializer.validated_data)
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
        
        

