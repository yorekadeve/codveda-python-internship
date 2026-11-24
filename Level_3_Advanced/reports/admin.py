from django.contrib import admin

from .models import ScamReport


@admin.register(ScamReport)
class ScamReportAdmin(admin.ModelAdmin):
    list_display = ("indicator_value", "scam_type", "status", "reporter", "created_at")
    list_filter = ("status", "scam_type", "indicator_type")
    search_fields = ("indicator_value", "normalized_value", "description")
    readonly_fields = ("normalized_value", "created_at")