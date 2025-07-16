from ninja import Router
from app.auth import JWTAuth
from rustore.models import RustoreVersion
from rustore.schemas import VersionSchema

router = Router()
jwt_auth = JWTAuth()


@router.get(
    "/version",
    response=VersionSchema,
    summary="Получение версии приложения",
    auth=jwt_auth,
)
async def get_version(request):
    """
    Получение версии мобильного приложения.
    Возвращает версию мобильного приложения в виде целого числа.
    Только для мобильного приложения Rustore.
    """

    try:
        version = await RustoreVersion.objects.alatest("versionCode")
        return VersionSchema(
            versionCode=version.versionCode, versionName=version.versionName
        )
    except RustoreVersion.DoesNotExist:
        return VersionSchema(versionCode=0, versionName="0.0.0")
