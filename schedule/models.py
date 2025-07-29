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
