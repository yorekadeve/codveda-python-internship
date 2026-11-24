from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from audit.models import AuditLog

PASSWORD = "Str0ng-Test-Pass!"
FAST_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class AccountTests(TestCase):
    def setUp(self):
        cache.clear()

    def register(self, **overrides):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        data.update(overrides)
        return self.client.post(reverse("register"), data)

    def test_weak_password_is_rejected(self):
        response = self.register(password1="abc123", password2="abc123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_email_is_rejected_whatever_the_case(self):
        User.objects.create_user("first", "new@example.com", PASSWORD)
        response = self.register(username="second", email="NEW@example.com")
        self.assertContains(response, "already exists")
        self.assertEqual(User.objects.count(), 1)

    def test_registration_logs_the_user_in(self):
        response = self.register()
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_registration_is_rate_limited(self):
        for _ in range(5):
            self.assertEqual(self.register(password1="x", password2="x").status_code, 200)
        self.assertEqual(self.register(password1="x", password2="x").status_code, 429)

    def test_logout_needs_a_post(self):
        User.objects.create_user("someone", "s@example.com", PASSWORD)
        self.client.login(username="someone", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_account_locks_after_five_failed_logins(self):
        User.objects.create_user("victim", "v@example.com", PASSWORD)
        for _ in range(5):
            response = self.client.post(
                reverse("login"), {"username": "victim", "password": "wrong"}
            )
            self.assertContains(response, "Please enter a correct username and password")

        response = self.client.post(
            reverse("login"), {"username": "victim", "password": PASSWORD}
        )
        self.assertContains(response, "Too many failed attempts")
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(AuditLog.objects.filter(action="login_locked").exists())

    def test_lockout_only_affects_the_attacked_username(self):
        User.objects.create_user("victim", "v@example.com", PASSWORD)
        User.objects.create_user("alice", "a@example.com", PASSWORD)
        for _ in range(5):
            self.client.post(reverse("login"), {"username": "victim", "password": "wrong"})

        response = self.client.post(
            reverse("login"), {"username": "alice", "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_logins_are_audited_with_ip_address(self):
        User.objects.create_user("victim", "v@example.com", PASSWORD)
        self.client.post(reverse("login"), {"username": "victim", "password": "wrong"})
        self.client.post(reverse("login"), {"username": "victim", "password": PASSWORD})
        failed = AuditLog.objects.get(action="login_failed")
        self.assertEqual(failed.ip_address, "127.0.0.1")
        self.assertTrue(AuditLog.objects.filter(action="login").exists())

    def test_password_reset_link_works_only_once(self):
        user = User.objects.create_user("resetme", "reset@example.com", PASSWORD)
        response = self.client.post(reverse("password_reset"), {"email": "reset@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)

        link = next(
            line for line in mail.outbox[0].body.splitlines() if line.startswith("http")
        )
        path = urlparse(link).path

        response = self.client.get(path, follow=True)
        set_password_url = response.redirect_chain[-1][0]
        new_password = "Another-Str0ng-Pass!"
        response = self.client.post(
            set_password_url,
            {"new_password1": new_password, "new_password2": new_password},
        )
        self.assertRedirects(response, reverse("password_reset_complete"))
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

        response = self.client.get(path, follow=True)
        self.assertContains(response, "invalid or has expired")

    def test_reset_does_not_reveal_unknown_emails(self):
        response = self.client.post(reverse("password_reset"), {"email": "nobody@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)