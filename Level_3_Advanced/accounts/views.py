from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.shortcuts import redirect, render

from audit.throttle import rate_limit
from audit.utils import get_client_ip, log_event

from .forms import RegisterForm

MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 15 * 60


def home(request):
    return render(request, "home.html")


@rate_limit("register", 5, 3600, methods=("POST",))
def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_event("registered", request=request, actor=user)
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/form.html",
        {"form": form, "title": "Create your account", "button": "Register"},
    )


class SecureLoginView(LoginView):
    template_name = "accounts/form.html"
    extra_context = {"title": "Log in", "button": "Log in", "is_login": True}

    def _lock_key(self, request):
        username = request.POST.get("username", "").strip().lower()[:150]
        return f"loginfail:{get_client_ip(request)}:{username}"

    def post(self, request, *args, **kwargs):
        if cache.get(self._lock_key(request), 0) >= MAX_FAILED_LOGINS:
            username = request.POST.get("username", "")[:50]
            log_event("login_locked", request=request, details=f"username: {username}")
            messages.error(
                request, "Too many failed attempts. Please try again in 15 minutes."
            )
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._lock_key(self.request)
        cache.add(key, 0, timeout=LOCKOUT_SECONDS)
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=LOCKOUT_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._lock_key(self.request))
        return super().form_valid(form)