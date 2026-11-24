from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from .utils import log_event


@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    log_event("login", request=request, actor=user)


@receiver(user_logged_out)
def record_logout(sender, request, user, **kwargs):
    log_event("logout", request=request, actor=user)


@receiver(user_login_failed)
def record_failed_login(sender, credentials, request=None, **kwargs):
    username = str(credentials.get("username", ""))[:50]
    log_event("login_failed", request=request, details=f"username: {username}")