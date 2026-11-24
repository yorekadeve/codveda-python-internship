from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .models import AuditLog
from .utils import log_event

PASSWORD = "Str0ng-Test-Pass!"
FAST_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class AuditTests(TestCase):
    def test_log_event_records_and_trims_details(self):
        user = User.objects.create_user("someone", "s@example.com", PASSWORD)
        log_event("test_action", actor=user, target="report:1", details="x" * 600)
        entry = AuditLog.objects.get(action="test_action")
        self.assertEqual(entry.actor, user)
        self.assertEqual(entry.target, "report:1")
        self.assertEqual(len(entry.details), 500)

    def test_audit_log_cannot_be_added_or_deleted_in_admin(self):
        boss = User.objects.create_superuser("boss", "boss@example.com", PASSWORD)
        self.client.force_login(boss)
        entry = AuditLog.objects.create(action="test")
        self.assertEqual(self.client.get("/admin/audit/auditlog/add/").status_code, 403)
        delete_url = f"/admin/audit/auditlog/{entry.pk}/delete/"
        self.assertEqual(self.client.get(delete_url).status_code, 403)