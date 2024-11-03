from django.db import models
    
class clients(models.Model):
    client_name = models.CharField(max_length=255, unique=True)
    is_teacher = models.BooleanField()
    
    class Meta:
        db_table = 'clients'

    def __str__(self):
        return self.client_name


class schedules(models.Model):
    client = models.ForeignKey(clients, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()

    class Meta:
        unique_together = ('client', 'date')
        db_table = 'schedules'

    def __str__(self):
        return f"Schedule for {self.client} on {self.date}"


class classes(models.Model):
    schedule = models.ForeignKey(schedules, on_delete=models.CASCADE, related_name='classes')
    number = models.IntegerField()
    title = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    partner = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('schedule', 'number')
        db_table = 'classes'

    def __str__(self):
        return f"{self.title} (Class {self.number})"