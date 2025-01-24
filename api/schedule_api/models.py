from django.db import models
    
    
class Client(models.Model):
    client_name = models.CharField(max_length=255)
    is_teacher = models.BooleanField(default=False)

    class Meta:
        ordering = ['client_name']

class Schedule(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    
    class Meta:
        ordering = ['date']

class Lesson(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='lessons')
    number = models.IntegerField()
    
    class Meta:
        ordering = ['number']

class ItemLesson(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    partner = models.CharField(max_length=255)
    location = models.CharField(max_length=50, null=True, blank=True)
    
    

class User(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    is_super_admin = models.BooleanField(default=False)

    
    