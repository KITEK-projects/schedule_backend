
from django.core.cache import cache


def clear_all_cache():
    """
    Удаляет весь кеш апи
    """
    cache.clear()