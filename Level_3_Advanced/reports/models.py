import uuid
from pathlib import Path

from django.conf import settings
from django.db import models

from .utils import normalize_indicator


def evidence_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"evidence/{uuid.uuid4().hex}{extension}"


class ScamReport(models.Model):
    class ScamType(models.TextChoices):
        MOBILE_MONEY = "mobile_money", "Mobile money scam"
        FAKE_SMS = "fake_sms", "Fake SMS or message"
        FAKE_JOB = "fake_job", "Fake job offer"
        INVESTMENT = "investment", "Investment or pyramid scam"
        ROMANCE = "romance", "Romance scam"
        PHISHING = "phishing", "Phishing link"
        OTHER = "other", "Other"

    class IndicatorType(models.TextChoices):
        PHONE = "phone", "Phone number"
        LINK = "link", "Website link"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports"
    )
    scam_type = models.CharField(max_length=20, choices=ScamType.choices)
    indicator_type = models.CharField(max_length=10, choices=IndicatorType.choices)
    indicator_value = models.CharField(max_length=255)
    normalized_value = models.CharField(max_length=255, db_index=True, editable=False)
    description = models.TextField(max_length=2000)
    message_text = models.TextField(max_length=2000, blank=True)
    amount_lost = models.PositiveIntegerField(null=True, blank=True)
    date_occurred = models.DateField()
    evidence = models.ImageField(upload_to=evidence_upload_path, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.normalized_value = normalize_indicator(
            self.indicator_type, self.indicator_value
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_scam_type_display()}: {self.indicator_value} ({self.get_status_display()})"