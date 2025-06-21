from django.db import models

class RustoreVersion(models.Model):
    versionName = models.CharField(max_length=50, unique=True)
    versionCode = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return str(self.versionCode)

    class Meta:
        ordering = ["-versionCode"]