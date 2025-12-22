from rest_framework.routers import DefaultRouter
from .views import WatchlistViewSet

router = DefaultRouter()
router.register(r'watchlists', WatchlistViewSet, basename='watchlist')

urlpatterns = router.urls