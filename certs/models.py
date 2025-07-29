from django.db import models

from my_user.models import MyUser


class Cert(models.Model):
    class STATUS(models.TextChoices):
        AT_WORK = "AW", ("В работе")
        READY = "RY", ("Готово")
        
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    group = models.CharField(max_length=16, verbose_name="Группа")
    requested_by = models.CharField(max_length=150, verbose_name="Требуется для")
    quantity = models.IntegerField(verbose_name="Колличество")
    status = models.CharField(
        choices=STATUS, default=STATUS.AT_WORK, verbose_name="Статус"
    )

    def __str__(self):
        return f"{self.group} — {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Справка"
        verbose_name_plural = "Справки"
