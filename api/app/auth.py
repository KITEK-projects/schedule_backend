from ninja.security import HttpBearer
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            return (
                user
            )
        except Exception:
            return None
