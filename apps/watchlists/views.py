from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.accounts.permissions import HasMultipleWatchlists
from .models import Watchlist, WatchlistItem
from .serializers import WatchlistSerializer, WatchlistItemSerializer


class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated, HasMultipleWatchlists]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).prefetch_related('items__stock')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-stocks')
    @transaction.atomic
    def add_stocks(self, request, pk):
        watchlist = self.get_object()
        stock_ids = request.data.get('stock_ids', [])
        if not isinstance(stock_ids, list):
            return Response({"error": "stock_ids must be a list"}, status=400)

        created = []
        for stock_id in stock_ids:
            _, item_created = WatchlistItem.objects.get_or_create(
                watchlist=watchlist,
                stock_id=stock_id
            )
            if item_created:
                created.append(stock_id)

        return Response({"added": created})

    @action(detail=True, methods=['post'], url_path='remove-stocks')
    @transaction.atomic
    def remove_stocks(self, request, pk):
        watchlist = self.get_object()
        stock_ids = request.data.get('stock_ids', [])
        deleted, _ = WatchlistItem.objects.filter(
            watchlist=watchlist,
            stock_id__in=stock_ids
        ).delete()
        return Response({"removed_count": deleted})