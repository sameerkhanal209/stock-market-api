from django.db import models
from django.utils import timezone


class StockManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)


class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = StockManager()

    class Meta:
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['exchange']),
        ]
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockPriceQuerySet(models.QuerySet):
    def latest_for_stock(self, stock_id):
        return self.filter(stock_id=stock_id).order_by('-timestamp').first()

    def in_date_range(self, stock_id, start_date, end_date=None):
        qs = self.filter(stock_id=stock_id)
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        return qs.order_by('timestamp')

    def aggregates(self, stock_id, start_date=None, end_date=None):
        qs = self.in_date_range(stock_id, start_date, end_date)
        if not qs.exists():
            return None
        from django.db.models import Min, Max, Avg, StdDev
        return qs.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            volatility=StdDev('price'),
        )


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=12, decimal_places=4)
    source = models.CharField(max_length=100, default="external_api")
    timestamp = models.DateTimeField(db_index=True)

    objects = StockPriceQuerySet.as_manager()

    class Meta:
        unique_together = ('stock', 'timestamp')  # Prevent duplicates
        indexes = [
            models.Index(fields=['stock', '-timestamp']),  # Critical for latest + range queries
            models.Index(fields=['timestamp']),
        ]
        verbose_name = "Stock Price"
        verbose_name_plural = "Stock Prices"

    def __str__(self):
        return f"{self.stock.symbol} @ {self.timestamp} = {self.price}"

    @property
    def is_latest(self):
        return self == self.stock.prices.latest_for_stock(self.stock_id)