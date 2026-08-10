from django.core.cache import cache
from django.http import HttpResponse


class AdminLoginThrottleMiddleware:
    """Rate-limits POST attempts to the Django admin login page by IP.

    Django's built-in admin has no brute-force protection of its own, unlike
    the site's own /api/auth/login/, which is throttled via DRF and locks
    per-account after repeated failures. This closes the same gap for the
    one login form DRF's throttling classes can't reach.
    """

    LIMIT = 15
    WINDOW_SECONDS = 60 * 60
    ADMIN_LOGIN_PATH = "/admin/login/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path == self.ADMIN_LOGIN_PATH:
            key = f"admin-login-throttle:{self._client_ip(request)}"
            attempts = cache.get(key, 0)
            if attempts >= self.LIMIT:
                return HttpResponse(
                    "Too many login attempts. Please try again later.",
                    status=429,
                    content_type="text/plain",
                )
            cache.set(key, attempts + 1, self.WINDOW_SECONDS)
        return self.get_response(request)

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
