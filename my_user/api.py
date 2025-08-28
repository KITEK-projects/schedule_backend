from ninja import Router
from ninja_jwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import get_user_model

from app.auth import JWTAuth
from .schemas import UserCreate, TokenResponse, UserOut, UserUpdate
from ninja.errors import HttpError
from django.http import HttpRequest


from .models import ROLE_CHOICES, MyUser

router = Router()
jwt_auth = JWTAuth()
User = get_user_model()


@router.post("", response=TokenResponse)
def add_user(request, data: UserCreate):
    """Создание пользователя"""
    if MyUser.objects.filter(username=data.username).exists():
        raise HttpError(400, "Пользователь с таким username уже существует")

    user = MyUser.objects.create_user(
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        password=data.password,  # Хешируется автоматически
    )

    refresh = str(RefreshToken.for_user(user))
    access = str(AccessToken.for_user(user))
    return TokenResponse(success=True, access=access, refresh=refresh)


@router.get("", auth=jwt_auth, response=UserOut)
def retrieve_user(request, username: str) -> UserOut:
    """Получение пользователя по username"""
    user = MyUser.objects.filter(username=username).first()
    if not user:
        raise HttpError(404, "Пользователь не найден")

    user_out = UserOut.from_orm(user)
    user_out.role = user.get_role_display()
    return user_out


@router.delete("", auth=jwt_auth)
def delete_user(request: HttpRequest):
    """Удаление пользователя"""
    user = request.auth
    user.delete()
    return {"detail": "Пользователь успешно удален"}


@router.put("", auth=jwt_auth)
def update_user(request, data: UserUpdate):
    user = request.auth

    update_fields = []
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
        update_fields.append(field)

    if update_fields:
        user.save(update_fields=update_fields)

    return {"detail": "Пользователь успешно обновлен"}


@router.put("role", auth=jwt_auth)
def update_user_role(request: HttpRequest, username: str, role: str):
    admin = request.auth

    if admin.role != ROLE_CHOICES.ADMIN:
        raise HttpError(403, "Сюда можно только Admin")

    user = User.objects.filter(username=username).first()

    if not user:
        raise HttpError(404, "Пользователь не найден")

    role_choice_value = None
    for i in ROLE_CHOICES:
        if i.label == role:
            role_choice_value = i.value
    if not role_choice_value:
        raise HttpError(400, f"Роль '{role}' невалидна")

    user.role = role_choice_value
    user.save()

    return {
        "username": user.username,
        "new_role": user.get_role_display(),
    }
