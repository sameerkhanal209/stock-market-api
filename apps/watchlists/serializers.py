from rest_framework import serializers
from .models import Watchlist, WatchlistItem
from apps.stocks.serializers import StockSerializer
from apps.stocks.models import Stock

class WatchlistItemSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.active(), source='stock', write_only=True
    )

    class Meta:
        model = WatchlistItem
        fields = ['stock', 'stock_id', 'added_at', 'alert_thresholds']


class WatchlistSerializer(serializers.ModelSerializer):
    items = WatchlistItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'is_default', 'created_at', 'items', 'item_count']