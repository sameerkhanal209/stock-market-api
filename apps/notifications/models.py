from django.db import models
from django.contrib.auth import get_user_model
from apps.stocks.models import Stock

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['read']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class WebhookSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.URLField(max_length=500)
    event_type = models.CharField(max_length=50, choices=[
        ('price_alert', 'Price Alert'),
        ('price_update', 'Price Update'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'endpoint', 'event_type')