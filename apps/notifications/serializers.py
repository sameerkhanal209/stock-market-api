from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'stock_symbol', 'read', 'created_at']
        read_only_fields = ['id', 'title', 'message', 'stock_symbol', 'created_at']