from django.db import models
from django.contrib.auth import get_user_model
from apps.stocks.models import Stock

User = get_user_model()


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Watchlist.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    alert_thresholds = models.JSONField(default=dict, blank=True)  # e.g. {"upper": 100, "lower": 50}

    class Meta:
        unique_together = ('watchlist', 'stock')
        indexes = [
            models.Index(fields=['watchlist']),
            models.Index(fields=['stock']),
        ]

    def __str__(self):
        return f"{self.watchlist.name} - {self.stock.symbol}"