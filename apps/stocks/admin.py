from django.contrib import admin
from .models import Stock, StockPrice

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'exchange', 'is_active')
    search_fields = ('symbol', 'name')
    list_filter = ('exchange', 'is_active')

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'price', 'timestamp', 'source')
    list_filter = ('source',)
    readonly_fields = ('stock', 'price', 'source', 'timestamp')