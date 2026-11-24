import os
import shutil
import tempfile
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import Group, Permission, User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from audit.models import AuditLog

from .models import Corroboration, ScamReport
from .stats import headline_stats
from .utils import normalize_indicator

TEMP_MEDIA = tempfile.mkdtemp()
PASSWORD = "Str0ng-Test-Pass!"
FAST_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA, ignore_errors=True)


def make_user(username, moderator=False):
    user = User.objects.create_user(username, f"{username}@example.com", PASSWORD)
    if moderator:
        group, _ = Group.objects.get_or_create(name="Moderators")
        group.permissions.add(Permission.objects.get(codename="review_reports"))
        user.groups.add(group)
    return user


def make_image_file(name="shot.png", image_format="PNG"):
    buffer = BytesIO()
    Image.new("RGB", (2, 2), "red").save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def make_report(reporter, value="0772123456", indicator_type="phone", status="pending", **extra):
    return ScamReport.objects.create(
        reporter=reporter,
        scam_type="mobile_money",
        indicator_type=indicator_type,
        indicator_value=value,
        description="Test description",
        date_occurred=timezone.localdate(),
        status=status,
        **extra,
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA, PASSWORD_HASHERS=FAST_HASHERS)
class BaseTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.reporter = make_user("reporter")
        self.other = make_user("other")
        self.moderator = make_user("moderator", moderator=True)

    def login(self, user):
        self.client.login(username=user.username, password=PASSWORD)


class NormalizationTests(TestCase):
    def test_phone_formats_all_match(self):
        variants = [
            "0772123456",
            "+256772123456",
            "0772 123 456",
            "772123456",
            "00256772123456",
            "(0772) 123-456",
        ]
        for variant in variants:
            self.assertEqual(normalize_indicator("phone", variant), "+256772123456", variant)

    def test_invalid_phone_gives_empty_result(self):
        self.assertEqual(normalize_indicator("phone", "12345"), "")

    def test_link_formats_all_match(self):
        variants = [
            "scam-site.com/win-prize",
            "www.SCAM-SITE.com/win-prize/",
            "https://scam-site.com/win-prize",
            "http://www.Scam-Site.com/win-prize/",
        ]
        for variant in variants:
            self.assertEqual(normalize_indicator("link", variant), "scam-site.com/win-prize", variant)

    def test_invalid_link_gives_empty_result(self):
        self.assertEqual(normalize_indicator("link", "localhost"), "")


class AccessControlTests(BaseTestCase):
    def test_anonymous_users_are_sent_to_login(self):
        for name in ["submit_report", "my_reports", "moderation_queue"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse("login"), response.url)

    def test_regular_user_cannot_open_moderation_queue(self):
        self.login(self.reporter)
        self.assertEqual(self.client.get(reverse("moderation_queue")).status_code, 403)

    def test_moderator_can_open_moderation_queue(self):
        self.login(self.moderator)
        self.assertEqual(self.client.get(reverse("moderation_queue")).status_code, 200)

    def test_owner_can_view_own_report(self):
        report = make_report(self.reporter)
        self.login(self.reporter)
        response = self.client.get(reverse("report_detail", args=[report.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_someone_elses_report(self):
        report = make_report(self.reporter)
        self.login(self.other)
        response = self.client.get(reverse("report_detail", args=[report.pk]))
        self.assertEqual(response.status_code, 404)

    def test_evidence_is_private(self):
        report = make_report(self.reporter, evidence=make_image_file())
        url = reverse("evidence_file", args=[report.pk])

        self.assertEqual(self.client.get(url).status_code, 302)

        self.login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)

        self.login(self.reporter)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"".join(response.streaming_content).startswith(b"\x89PNG"))

        self.login(self.moderator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"".join(response.streaming_content).startswith(b"\x89PNG"))
        self.assertTrue(AuditLog.objects.filter(action="evidence_viewed").exists())


class ModerationTests(BaseTestCase):
    def test_moderator_can_verify(self):
        report = make_report(self.reporter)
        self.login(self.moderator)
        response = self.client.post(reverse("review_report", args=[report.pk]), {"action": "verify"})
        self.assertRedirects(response, reverse("moderation_queue"))
        report.refresh_from_db()
        self.assertEqual(report.status, "verified")
        self.assertEqual(report.reviewed_by, self.moderator)
        self.assertTrue(AuditLog.objects.filter(action="report_verified").exists())

    def test_reject_needs_a_reason(self):
        report = make_report(self.reporter)
        self.login(self.moderator)
        response = self.client.post(
            reverse("review_report", args=[report.pk]),
            {"action": "reject", "rejection_reason": "   "},
        )
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, "pending")

    def test_reject_with_reason(self):
        report = make_report(self.reporter)
        self.login(self.moderator)
        self.client.post(
            reverse("review_report", args=[report.pk]),
            {"action": "reject", "rejection_reason": "Not enough detail"},
        )
        report.refresh_from_db()
        self.assertEqual(report.status, "rejected")
        self.assertEqual(report.rejection_reason, "Not enough detail")

    def test_regular_user_cannot_review(self):
        report = make_report(self.reporter)
        self.login(self.other)
        response = self.client.post(reverse("review_report", args=[report.pk]), {"action": "verify"})
        self.assertEqual(response.status_code, 403)
        report.refresh_from_db()
        self.assertEqual(report.status, "pending")

    def test_moderator_cannot_review_own_report(self):
        report = make_report(self.moderator)
        self.login(self.moderator)
        self.client.post(reverse("review_report", args=[report.pk]), {"action": "verify"})
        report.refresh_from_db()
        self.assertEqual(report.status, "pending")

    def test_unknown_action_is_a_bad_request(self):
        report = make_report(self.reporter)
        self.login(self.moderator)
        response = self.client.post(reverse("review_report", args=[report.pk]), {"action": "delete"})
        self.assertEqual(response.status_code, 400)


class CheckerTests(BaseTestCase):
    def search(self, query):
        return self.client.get(reverse("check_scam"), {"q": query})

    def test_verified_report_matches_every_phone_format(self):
        make_report(self.reporter, status="verified")
        for query in ["0772123456", "+256772123456", "0772 123 456", "772123456"]:
            self.assertContains(self.search(query), "Verified scam")

    def test_pending_report_shows_cautious_message(self):
        make_report(self.reporter, status="pending")
        self.assertContains(self.search("0772123456"), "Reported, not yet verified")

    def test_rejected_report_is_not_public(self):
        make_report(self.reporter, status="rejected")
        self.assertContains(self.search("0772123456"), "No reports found")

    def test_unknown_number_has_no_reports(self):
        self.assertContains(self.search("0701999888"), "No reports found")

    def test_invalid_input_is_explained(self):
        self.assertContains(self.search("abc"), "does not look like")

    def test_domain_report_covers_every_page_but_page_report_does_not_cover_domain(self):
        make_report(self.reporter, "scam-site.com", indicator_type="link", status="verified")
        self.assertContains(self.search("www.scam-site.com/win-prize"), "Verified scam")

        ScamReport.objects.all().delete()
        make_report(self.reporter, "scam-site.com/win-prize", indicator_type="link", status="verified")
        self.assertContains(self.search("scam-site.com"), "No reports found")

    def test_public_page_hides_private_details(self):
        report = make_report(self.reporter, status="verified")
        report.description = "SECRET-DETAIL-TEXT"
        report.save()
        response = self.search("0772123456")
        self.assertNotContains(response, "SECRET-DETAIL-TEXT")
        self.assertNotContains(response, "reporter@example.com")

    def test_search_is_rate_limited(self):
        for _ in range(30):
            self.assertEqual(self.search("0701000000").status_code, 200)
        self.assertEqual(self.search("0701000000").status_code, 429)


class StatsTests(BaseTestCase):
    def test_only_verified_reports_are_counted(self):
        make_report(self.reporter, "0772123456", status="verified", amount_lost=50000)
        make_report(self.other, "0772123456", status="verified", amount_lost=20000)
        make_report(self.reporter, "0701000111", status="pending", amount_lost=999999)
        make_report(self.reporter, "0701000222", status="rejected", amount_lost=999999)
        stats = headline_stats()
        self.assertEqual(stats["verified_reports"], 2)
        self.assertEqual(stats["flagged_count"], 1)
        self.assertEqual(stats["total_lost"], 70000)

    def test_statistics_page_is_public(self):
        self.assertEqual(self.client.get(reverse("statistics")).status_code, 200)


class ConfirmationTests(BaseTestCase):
    def test_user_can_confirm_only_once(self):
        report = make_report(self.reporter, status="verified")
        self.login(self.other)
        url = reverse("confirm_report", args=[report.pk])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Corroboration.objects.filter(report=report).count(), 1)

    def test_cannot_confirm_own_report(self):
        report = make_report(self.reporter, status="verified")
        self.login(self.reporter)
        self.client.post(reverse("confirm_report", args=[report.pk]))
        self.assertEqual(Corroboration.objects.count(), 0)

    def test_confirming_needs_a_post(self):
        report = make_report(self.reporter, status="verified")
        self.login(self.other)
        response = self.client.get(reverse("confirm_report", args=[report.pk]))
        self.assertEqual(response.status_code, 405)

    def test_cannot_confirm_rejected_report(self):
        report = make_report(self.reporter, status="rejected")
        self.login(self.other)
        response = self.client.post(reverse("confirm_report", args=[report.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Corroboration.objects.count(), 0)

    def test_visitor_cannot_confirm(self):
        report = make_report(self.reporter, status="verified")
        response = self.client.post(reverse("confirm_report", args=[report.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Corroboration.objects.count(), 0)


class UploadValidationTests(BaseTestCase):
    def form_data(self, **overrides):
        data = {
            "scam_type": "mobile_money",
            "indicator_type": "phone",
            "indicator_value": "0772123456",
            "description": "Test",
            "message_text": "",
            "amount_lost": "",
            "date_occurred": timezone.localdate().isoformat(),
        }
        data.update(overrides)
        return data

    def submit(self, **overrides):
        self.login(self.reporter)
        return self.client.post(reverse("submit_report"), self.form_data(**overrides))

    def test_valid_report_is_saved_as_pending(self):
        response = self.submit()
        self.assertRedirects(response, reverse("my_reports"))
        report = ScamReport.objects.get()
        self.assertEqual(report.status, "pending")
        self.assertEqual(report.reporter, self.reporter)
        self.assertEqual(report.normalized_value, "+256772123456")

    def test_reporter_comes_from_session_not_from_form(self):
        self.submit(reporter=self.other.pk)
        self.assertEqual(ScamReport.objects.get().reporter, self.reporter)

    def test_bad_phone_number_is_rejected(self):
        response = self.submit(indicator_value="12345")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ScamReport.objects.count(), 0)

    def test_future_date_is_rejected(self):
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.submit(date_occurred=tomorrow)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ScamReport.objects.count(), 0)

    def test_fake_image_is_rejected(self):
        fake = SimpleUploadedFile("fake.png", b"not an image", content_type="image/png")
        self.submit(evidence=fake)
        self.assertEqual(ScamReport.objects.count(), 0)

    def test_oversized_image_is_rejected(self):
        buffer = BytesIO()
        Image.frombytes("RGB", (1000, 1000), os.urandom(3 * 1000 * 1000)).save(buffer, format="PNG")
        self.assertGreater(len(buffer.getvalue()), 2 * 1024 * 1024)
        big = SimpleUploadedFile("big.png", buffer.getvalue(), content_type="image/png")
        self.submit(evidence=big)
        self.assertEqual(ScamReport.objects.count(), 0)

    def test_wrong_image_format_is_rejected(self):
        gif_named_png = make_image_file(name="x.png", image_format="GIF")
        self.submit(evidence=gif_named_png)
        self.assertEqual(ScamReport.objects.count(), 0)

    def test_uploaded_file_gets_a_random_name(self):
        self.submit(evidence=make_image_file(name="my-private-photo.png"))
        report = ScamReport.objects.get()
        self.assertTrue(report.evidence.name.startswith("evidence/"))
        self.assertNotIn("my-private-photo", report.evidence.name)