from rest_framework.throttling import UserRateThrottle

class StandardUserThrottle(UserRateThrottle):
    scope = 'standard'

    def allow_request(self, request, view):
        if request.user.is_authenticated and request.user.tier == request.user.Tier.STANDARD:
            self.rate = self.get_rate() or '200/day'
            self.scope = 'standard'
            return super().allow_request(request, view)
        return True