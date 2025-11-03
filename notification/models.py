from django.db import models

from schedule.models import Client


class FCMToken(models.Model):
    token = models.TextField(unique=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="fcm_tokens",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.token} ({self.client.client_name})"
