from rest_framework import serializers
from .models import Stock, StockPrice


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'exchange', 'currency', 'is_active', 'created_at', 'created']
        read_only_fields = ['created_at', 'created']


class StockPriceSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)

    class Meta:
        model = StockPrice
        fields = ['price', 'timestamp', 'source', 'stock_symbol']
        read_only_fields = ['source']


class StockAggregateSerializer(serializers.Serializer):
    min_price = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    avg_price = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    volatility = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    count = serializers.IntegerField()