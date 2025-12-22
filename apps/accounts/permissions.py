from rest_framework import permissions
from datetime import timedelta
from django.utils import timezone


class IsAdmin(permissions.BasePermission):
    """Only Admin tier allowed"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.tier == request.user.Tier.ADMIN
        )


class IsPremiumOrAdmin(permissions.BasePermission):
    """Premium or Admin tier"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.tier in (request.user.Tier.PREMIUM, request.user.Tier.ADMIN)
        )


class CanAccessFullHistory(permissions.BasePermission):
    """
    Allows access to historical data beyond 30 days
    Only for Premium/Admin users
    """
    def has_object_permission(self, request, view, obj):
        # For list views, check query params
        start_date = request.query_params.get('start_date')
        if start_date:
            try:
                from_date = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if (timezone.now() - from_date) > timedelta(days=30):
                    return request.user.tier in (request.user.Tier.PREMIUM, request.user.Tier.ADMIN)
            except ValueError:
                pass
        return True  # If no date or invalid, allow (safe default)


class HasMultipleWatchlists(permissions.BasePermission):
    """Premium/Admin can create more than one watchlist"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            user = request.user
            if user.tier in (user.Tier.PREMIUM, user.Tier.ADMIN):
                return True
            # Standard users can have only 1 watchlist
            from apps.watchlists.models import Watchlist
            return Watchlist.objects.filter(user=user).count() == 0
        return True