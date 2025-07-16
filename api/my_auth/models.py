from django.db import models
from django.contrib.auth.models import AbstractUser

class ROLE_CHOICES(models.TextChoices):
        ANONYMOUS = "AS", ("anonymous")
        STUDENT = "ST", ("student")
        TEACHER = "TR", ("teacher")

class MyUser(AbstractUser):
    

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_CHOICES.ANONYMOUS
    )

    REQUIRED_FIELDS = ["first_name", "last_name"]


class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)
    curator = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': ROLE_CHOICES.TEACHER},
    )
    students = models.ManyToManyField(
        MyUser,
        related_name="student_groups",
        blank=True,
        limit_choices_to={'role': ROLE_CHOICES.STUDENT},
    )
