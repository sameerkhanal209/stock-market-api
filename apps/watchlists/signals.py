from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.stocks.models import StockPrice
from apps.notifications.models import Notification
from apps.watchlists.models import WatchlistItem
import requests
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

@receiver(post_save, sender=StockPrice)
def check_price_alerts(sender, instance, created, **kwargs):
    if not created:
        return  # Only on new prices

    stock = instance.stock
    price = instance.price

    # Find watchlist items with thresholds
    items = WatchlistItem.objects.filter(
        stock=stock,
        alert_thresholds__isnull=False
    ).exclude(alert_thresholds={})

    for item in items:
        thresholds = item.alert_thresholds
        user = item.watchlist.user
        triggered = []

        if thresholds.get('upper') and price >= Decimal(str(thresholds['upper'])):
            triggered.append(f"above {thresholds['upper']}")

        if thresholds.get('lower') and price <= Decimal(str(thresholds['lower'])):
            triggered.append(f"below {thresholds['lower']}")

        if triggered:
            message = f"{stock.symbol} is {', '.join(triggered)} at {price}"
            Notification.objects.create(
                user=user,
                title=f"Price Alert: {stock.symbol}",
                message=message,
                stock=stock
            )

            # Webhook delivery (fire and forget)
            for sub in user.webhooksubscription_set.filter(
                event_type='price_alert', is_active=True
            ):
                try:
                    requests.post(sub.endpoint, json={
                        'event': 'price_alert',
                        'stock': stock.symbol,
                        'price': float(price),
                        'message': message,
                        'timestamp': instance.timestamp.isoformat()
                    }, timeout=5)
                except Exception as e:
                    logger.error(f"Webhook failed: {e}")