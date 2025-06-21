from ninja import Router
from rustore.models import RustoreVersion


router = Router()

@router.get("/get_version/", response=int, summary="Получение версии приложения")
def get_version(request):
    """
    Получение версии мобильного приложения.
    Возвращает версию мобильного приложения в виде целого числа.
    Только для мобильного приложения Rustore.
    """
  
    try:
        version = RustoreVersion.objects.latest('versionCode')
        return version.versionCode
    except RustoreVersion.DoesNotExist:
        return 0