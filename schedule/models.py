from datetime import timedelta
from django.db import models
from django.utils.timezone import now


class Client(models.Model):
    client_name = models.CharField(max_length=255, unique=True)
    ascii_name = models.CharField(max_length=255, blank=True)
    is_teacher = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=now)

    def update_last_modified(self):
        self.last_update = now()
        self.save(update_fields=["last_update"])

    def __str__(self):
        return self.client_name


class ScheduleDay(models.Model):
    date = models.DateField()
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="schedule_days"
    )

    def __str__(self):
        return self.date.strftime("%d.%m.%Y")
    
    @property
    def week_day(self) -> int:
        return self.date.weekday()
    
    @property
    def format_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    class Meta:
        ordering = ["date"]
        unique_together = ("client", "date")


class Lesson(models.Model):
    schedule = models.ForeignKey(
        ScheduleDay, on_delete=models.CASCADE, related_name="lessons"
    )
    number = models.IntegerField()
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    partner = models.CharField(max_length=255)
    location = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ["title", "number"]


class ScheduleFile(models.Model):
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    schedule_file = models.FileField()


class TimeOfBell(models.Model):
    start_time = models.TimeField(
        default="08:45",
        help_text="Время начала первой пары"
    )
    lesson = models.PositiveIntegerField(default=90, help_text="Врема пары")
    use_curator_hour = models.BooleanField(default=True, help_text="Включать кураторский час по понедельникам")
    curator_hour = models.PositiveIntegerField(default=40, help_text="Время кураторского часа")
    lunch_break_offset = models.PositiveIntegerField(default=5, help_text="Смещение обеденного перерыва, по понедельникам")
    lunch_break = models.PositiveIntegerField(default=30, help_text="Время обеденного перерыва")
    break_after_1 = models.PositiveIntegerField(default=10, help_text="Перемена после первой пары")
    break_after_2 = models.PositiveIntegerField(default=10, help_text="Перемена после второй пары")
    break_after_3 = models.PositiveIntegerField(default=10, help_text="Перемена после третьей пары")
    break_after_4 = models.PositiveIntegerField(default=10, help_text="Перемена после четвертой пары")
    break_after_5 = models.PositiveIntegerField(default=5, help_text="Перемена после пятой пары")

    def get_start_timedelta(self) -> timedelta:
        """Переводит start_time в timedelta (удобно для расчётов)."""
        return timedelta(
            hours=self.start_time.hour,
            minutes=self.start_time.minute
        )
    