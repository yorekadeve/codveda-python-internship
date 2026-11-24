from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse

from .utils import get_client_ip, log_event


def rate_limit(name, limit, window_seconds, methods=None):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if methods is None or request.method in methods:
                key = f"ratelimit:{name}:{get_client_ip(request)}"
                cache.add(key, 0, timeout=window_seconds)
                try:
                    count = cache.incr(key)
                except ValueError:
                    cache.set(key, 1, timeout=window_seconds)
                    count = 1
                if count > limit:
                    log_event("rate_limited", request=request, details=name)
                    return HttpResponse(
                        "Too many requests. Please wait a few minutes and try again.",
                        status=429,
                    )
            return view(request, *args, **kwargs)

        return wrapper

    return decorator