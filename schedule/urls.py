from datetime import timedelta


def format_lesson(start: timedelta, end: timedelta) -> str:
    return "-".join(
        f"{t//3600:02}:{(t%3600)//60:02}"
        for t in (int(start.total_seconds()), int(end.total_seconds()))
    )


def course_flag(group: str) -> int:
    """
    Возвращает 0, если группа 1 или 2 курса,
    1 — если 3 или 4 курс.
    """
    for ch in group:
        if ch.isdigit():
            return 0 if int(ch) in (1, 2) else 1
    return 1