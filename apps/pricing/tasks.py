import yfinance as yf
from celery import shared_task
from django.core.cache import cache
from apps.stocks.models import Stock, StockPrice
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@shared_task
def ingest_stock_prices():
    """
    Periodic task to fetch latest prices for all active stocks
    """
    active_stocks = Stock.objects.active()
    logger.info(f"Starting price ingestion for {active_stocks.count()} stocks")

    for stock in active_stocks:
        try:
            ticker = yf.Ticker(stock.symbol)
            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                logger.warning(f"No data returned for {stock.symbol}")
                continue

            latest = data.iloc[-1]
            price = Decimal(str(latest['Close'])).quantize(Decimal('0.0001'))

            # Idempotent update
            obj, created = StockPrice.objects.update_or_create(
                stock=stock,
                timestamp__date=timezone.now().date(),
                defaults={
                    'price': price,
                    'source': 'yfinance',
                    'timestamp': timezone.now(),
                }
            )

            # Invalidate latest price cache
            cache_key = f"latest_price_{stock.id}"
            cache.delete(cache_key)
            cache.delete(f"{cache_key}_ts")

            logger.info(f"{'Created' if created else 'Updated'} price for {stock.symbol}: {price}")

        except Exception as e:
            logger.error(f"Error fetching {stock.symbol}: {str(e)}")

    return "Price ingestion completed"