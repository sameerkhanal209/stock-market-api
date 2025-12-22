from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from apps.accounts.permissions import IsAdmin, CanAccessFullHistory
from .models import Stock, StockPrice
from .serializers import StockSerializer, StockPriceSerializer, StockAggregateSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.active()
    serializer_class = StockSerializer
    lookup_field = 'symbol'
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], url_path='latest-price')
    def latest_price(self, request, symbol):
        stock = self.get_object()
        cache_key = f"latest_price_{stock.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response({"price": cached, "timestamp": cache.get(f"{cache_key}_ts")})

        latest = stock.prices.latest_for_stock(stock.id)
        if latest:
            cache.set(cache_key, float(latest.price), timeout=60)  # Cache 1 min
            cache.set(f"{cache_key}_ts", latest.timestamp.isoformat(), timeout=60)
            return Response({"price": float(latest.price), "timestamp": latest.timestamp})
        return Response({"detail": "No price data"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='historical')
    def historical(self, request, symbol):
        stock = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now())

        # Tier-based history limit
        if start_date:
            try:
                from_date = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if (timezone.now() - from_date) > timedelta(days=30):
                    if not CanAccessFullHistory().has_permission(request, self):
                        return Response(
                            {"error": "Premium or Admin required for history >30 days"},
                            status=status.HTTP_403_FORBIDDEN
                        )
            except ValueError:
                return Response({"error": "Invalid start_date format"}, status=400)

        prices = stock.prices.in_date_range(stock.id, start_date, end_date)
        page = self.paginate_queryset(prices)
        serializer = StockPriceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='aggregates')
    def aggregates(self, request, symbol):
        stock = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        agg = stock.prices.aggregates(stock.id, start_date, end_date)
        if not agg:
            return Response({"detail": "No data in range"}, status=404)

        agg['count'] = stock.prices.in_date_range(stock.id, start_date, end_date).count()
        serializer = StockAggregateSerializer(agg)
        return Response(serializer.data)