from django.apps import AppConfig

class PricingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pricing'
    label = 'pricing'

    def ready(self):
        from .tasks import ingest_stock_prices