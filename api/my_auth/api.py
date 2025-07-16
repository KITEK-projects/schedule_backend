from ninja import Router
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .schemas import UserCreate, TokenOut, UserUpdate
from ninja.errors import HttpError

from .models import MyUser

router = Router()
User = get_user_model()


@router.post("", response=TokenOut)
def add_user(request, data: UserCreate):
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Пользователь с таким username уже существует")

    user = MyUser.objects.create_user(
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        password=data.password,  # Хешируется автоматически
    )

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


@router.get("")
def get_user(request, data: UserUpdate):
    pass


@router.delete("")
def delete_user(request, data: UserUpdate):
    pass


@router.put("")
def update_user(request, data: UserUpdate):
    pass


@router.put("role")
def update_user_role(request):
    pass
