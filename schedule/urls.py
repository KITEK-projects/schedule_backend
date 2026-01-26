from datetime import timedelta


def format_lesson(start: timedelta, end: timedelta) -> str:
    return "-".join(
        f"{t//3600:02}:{(t%3600)//60:02}"
        for t in (int(start.total_seconds()), int(end.total_seconds()))
    )


def is_lower_course(group: str) -> bool:
    """
    Возвращает True, если группа 1 или 2 курса,
    False — если 3 или 4 курс.
    """
    for ch in group:
        if ch.isdigit():
            return True if int(ch) in (1, 2) else False
    return False