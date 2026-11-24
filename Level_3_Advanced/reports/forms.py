from pathlib import Path

from django import forms
from django.utils import timezone

from .models import ScamReport
from .utils import normalize_indicator

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_EVIDENCE_SIZE = 2 * 1024 * 1024


class ScamReportForm(forms.ModelForm):
    class Meta:
        model = ScamReport
        fields = [
            "scam_type",
            "indicator_type",
            "indicator_value",
            "description",
            "message_text",
            "amount_lost",
            "date_occurred",
            "evidence",
        ]
        widgets = {
            "date_occurred": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "message_text": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "scam_type": "What kind of scam was it?",
            "indicator_type": "What are you reporting?",
            "indicator_value": "Phone number or website link",
            "description": "What happened?",
            "message_text": "Scam message (optional)",
            "amount_lost": "Amount lost in UGX (optional)",
            "date_occurred": "Date it happened",
            "evidence": "Screenshot (optional)",
        }
        help_texts = {
            "indicator_value": "For phones use 0772123456 or +256772123456. For links, paste the full address.",
            "evidence": "JPG, PNG or WEBP, up to 2 MB. Hide your own private details first.",
        }

    def clean_date_occurred(self):
        date_occurred = self.cleaned_data["date_occurred"]
        if date_occurred > timezone.localdate():
            raise forms.ValidationError("The date cannot be in the future.")
        return date_occurred

    def clean_evidence(self):
        evidence = self.cleaned_data.get("evidence")
        if not evidence or not hasattr(evidence, "image"):
            return evidence
        if evidence.size > MAX_EVIDENCE_SIZE:
            raise forms.ValidationError("The screenshot must be 2 MB or smaller.")
        if Path(evidence.name).suffix.lower() not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Only JPG, PNG or WEBP images are allowed.")
        if evidence.image.format not in ALLOWED_FORMATS:
            raise forms.ValidationError("Only JPG, PNG or WEBP images are allowed.")
        return evidence

    def clean(self):
        cleaned_data = super().clean()
        indicator_type = cleaned_data.get("indicator_type")
        value = cleaned_data.get("indicator_value")
        if indicator_type and value and not normalize_indicator(indicator_type, value):
            if indicator_type == "phone":
                message = "Enter a valid phone number, like 0772123456 or +256772123456."
            else:
                message = "Enter a valid website link, like example.com/offer."
            self.add_error("indicator_value", message)
        return cleaned_data