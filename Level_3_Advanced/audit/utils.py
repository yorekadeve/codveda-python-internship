from .models import AuditLog


def get_client_ip(request):
    if request is None:
        return None
    return request.META.get("REMOTE_ADDR")


def log_event(action, request=None, actor=None, target="", details=""):
    if actor is None and request is not None:
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            actor = user

    AuditLog.objects.create(
        actor=actor,
        action=action,
        target=target[:100],
        details=details[:500],
        ip_address=get_client_ip(request),
    )