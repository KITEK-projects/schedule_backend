from django.db import models
from django.utils.timezone import now


class Client(models.Model):
    client_name = models.CharField(max_length=255, unique=True)
    is_teacher = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=now)

    def update_last_modified(self):
        self.last_update = now()
        self.save(update_fields=["last_update"])

    def __str__(self):
        return self.client_name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


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
        verbose_name = "День расписания"
        verbose_name_plural = "Дни расписания"


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
        verbose_name = "Пара"
        verbose_name_plural = "Пары"


class ScheduleFile(models.Model):
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    schedule_file = models.FileField()

    class Meta:
        verbose_name = "Файл с расписанием"
        verbose_name_plural = "Файлы с расписанием"


class ScheduleTimeType(models.Model):
    """
    Тип расписания. Например:
    - '1-2 курс, Понедельник'
    - '3-4 курс, Суббота'
    """
    code = models.SlugField(unique=True, help_text="Уникальный код, например 'lower_mon'")
    name = models.CharField(max_length=100, help_text="Название для админки")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Расписание звонков"
        verbose_name_plural = "Расписания звонков"


class Bell(models.Model):
    """
    Конкретный звонок для конкретного типа расписания.
    """
    schedule_type = models.ForeignKey(
        ScheduleTimeType,
        on_delete=models.CASCADE,
        related_name='bells'
    )
    lesson_number = models.PositiveSmallIntegerField(verbose_name="№ пары",
                                                     help_text="Номер пары (1-7)")

    display_text = models.CharField(
        max_length=50,
        help_text="Текст для вывода."
    )

    class Meta:
        ordering = ['schedule_type', 'lesson_number']
        unique_together = ('schedule_type', 'lesson_number')
        verbose_name = "Звонки"
        verbose_name_plural = "Звонки"

    def __str__(self):
        return self.display_text

