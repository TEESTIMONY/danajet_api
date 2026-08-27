import json
import logging
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

from django.conf import settings

logger = logging.getLogger(__name__)


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def verify_turnstile(token, remote_ip=""):
    """Verify a Cloudflare Turnstile token. Returns True when Turnstile is
    not configured (TURNSTILE_SECRET_KEY unset), so local/staging setups
    without a Turnstile site keep working."""
    if not settings.TURNSTILE_SECRET_KEY:
        return True
    if not token:
        return False

    payload = {"secret": settings.TURNSTILE_SECRET_KEY, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    data = urlparse.urlencode(payload).encode("utf-8")
    request_obj = urlrequest.Request(settings.TURNSTILE_VERIFY_URL, data=data, method="POST")

    try:
        with urlrequest.urlopen(request_obj, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
            return bool(result.get("success"))
    except (urlerror.URLError, ValueError, TimeoutError):
        logger.exception("Turnstile verification request failed")
        return False
