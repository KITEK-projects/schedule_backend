from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import os

def internal_api(view_func):
    @wraps(view_func)
    def wrapper(view_instance, request, *args, **kwargs):
        allowed_token = os.getenv('INTERNAL_API_TOKEN')
        request_token = request.headers.get('X-Internal-Token')
        
        if not request_token or request_token != allowed_token:
            return Response(
                {'error': 'Unauthorized access'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        return view_func(view_instance, request, *args, **kwargs)
    return wrapper