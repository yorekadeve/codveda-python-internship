from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import ScamReport


def headline_stats():
    verified = ScamReport.objects.filter(status=ScamReport.Status.VERIFIED)
    return {
        "verified_reports": verified.count(),
        "flagged_count": verified.values("indicator_type", "normalized_value")
        .distinct()
        .count(),
        "total_lost": verified.aggregate(total=Sum("amount_lost"))["total"] or 0,
    }


def detailed_stats():
    verified = ScamReport.objects.filter(status=ScamReport.Status.VERIFIED)
    stats = headline_stats()
    total = stats["verified_reports"]
    labels = dict(ScamReport.ScamType.choices)

    by_type = []
    rows = verified.values("scam_type").annotate(total=Count("id")).order_by("-total")
    for row in rows:
        by_type.append(
            {
                "label": labels.get(row["scam_type"], row["scam_type"]),
                "total": row["total"],
                "percent": round(row["total"] * 100 / total) if total else 0,
            }
        )

    top_indicators = list(
        verified.values("indicator_type", "normalized_value")
        .annotate(total=Count("id"))
        .order_by("-total", "normalized_value")[:5]
    )

    since = timezone.localdate() - timedelta(days=180)
    months = list(
        verified.filter(date_occurred__gte=since)
        .annotate(month=TruncMonth("date_occurred"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    peak = max((m["total"] for m in months), default=0)
    for month in months:
        month["percent"] = round(month["total"] * 100 / peak) if peak else 0

    stats.update(
        {"by_type": by_type, "top_indicators": top_indicators, "months": months}
    )
    return stats