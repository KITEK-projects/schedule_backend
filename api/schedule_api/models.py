from django.db import models
    
class Client(models.Model):
    client_name = models.CharField(max_length=255, unique=True)
    is_teacher = models.BooleanField()


class Schedule(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='schedule')
    date = models.DateField()

    class Meta:
        unique_together = ('client', 'date')


class Lesson(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='lesson')
    number = models.IntegerField()

    class Meta:
        ordering = ["number"]

class ItemLesson(models.Model):
    schedule = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='item_lesson')
    title = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    partner = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["title"]
    

class Users(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    is_super_admin = models.BooleanField(default=False)

    
    