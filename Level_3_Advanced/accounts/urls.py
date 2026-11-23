from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/form.html",
            extra_context={"title": "Log in", "button": "Log in", "is_login": True},
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/form.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
            extra_context={"title": "Reset your password", "button": "Send reset link"},
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/message.html",
            extra_context={
                "title": "Check your email",
                "message": "If an account exists for that email, a reset link has been sent. "
                "In development, the email appears in the terminal where the server is running.",
                "link_name": "home",
                "link_text": "Back to home",
            },
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/form.html",
            success_url=reverse_lazy("password_reset_complete"),
            extra_context={"title": "Choose a new password", "button": "Save new password"},
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/message.html",
            extra_context={
                "title": "Password changed",
                "message": "Your password has been updated. You can now log in.",
                "link_name": "login",
                "link_text": "Log in",
            },
        ),
        name="password_reset_complete",
    ),
]