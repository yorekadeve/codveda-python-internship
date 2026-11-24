from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Max
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ScamReportForm
from .models import ScamReport
from .utils import detect_indicator, lookup_values

REVIEW_PERMISSION = "reports.review_reports"


def check_scam(request):
    query = request.GET.get("q", "").strip()[:255]
    context = {"query": query}

    if query:
        indicator_type, normalized = detect_indicator(query)
        if not normalized:
            context["invalid"] = True
        else:
            reports = ScamReport.objects.filter(
                indicator_type=indicator_type,
                normalized_value__in=lookup_values(indicator_type, normalized),
            )
            verified = reports.filter(status=ScamReport.Status.VERIFIED)
            labels = dict(ScamReport.ScamType.choices)
            breakdown = (
                verified.values("scam_type")
                .annotate(total=Count("id"))
                .order_by("-total")
            )
            context["normalized"] = normalized
            context["verified_count"] = verified.count()
            context["pending_count"] = reports.filter(
                status=ScamReport.Status.PENDING
            ).count()
            context["type_breakdown"] = [
                {"label": labels.get(row["scam_type"], row["scam_type"]), "total": row["total"]}
                for row in breakdown
            ]
            context["last_reported"] = verified.aggregate(latest=Max("date_occurred"))["latest"]

    return render(request, "reports/check.html", context)


@login_required
def submit_report(request):
    if request.method == "POST":
        form = ScamReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            messages.success(
                request,
                "Thank you. Your report was submitted and is waiting for review.",
            )
            return redirect("my_reports")
    else:
        form = ScamReportForm()
    return render(request, "reports/report_form.html", {"form": form})


@login_required
def my_reports(request):
    reports = ScamReport.objects.filter(reporter=request.user)
    return render(request, "reports/my_reports.html", {"reports": reports})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(ScamReport, pk=pk, reporter=request.user)
    return render(request, "reports/report_detail.html", {"report": report})


@login_required
def evidence_file(request, pk):
    report = get_object_or_404(ScamReport, pk=pk)
    if report.reporter != request.user and not request.user.has_perm(REVIEW_PERMISSION):
        raise Http404
    if not report.evidence:
        raise Http404
    return FileResponse(report.evidence.open("rb"))


@login_required
@permission_required(REVIEW_PERMISSION, raise_exception=True)
def moderation_queue(request):
    current = request.GET.get("status", "pending")
    if current not in {"pending", "verified", "rejected"}:
        current = "pending"

    reports = (
        ScamReport.objects.filter(status=current)
        .select_related("reporter")
        .order_by("created_at")
    )
    counts = {
        "pending": ScamReport.objects.filter(status=ScamReport.Status.PENDING).count(),
        "verified": ScamReport.objects.filter(status=ScamReport.Status.VERIFIED).count(),
        "rejected": ScamReport.objects.filter(status=ScamReport.Status.REJECTED).count(),
    }
    return render(
        request,
        "reports/moderation_queue.html",
        {"reports": reports, "counts": counts, "current": current},
    )


@login_required
@permission_required(REVIEW_PERMISSION, raise_exception=True)
def review_report(request, pk):
    report = get_object_or_404(ScamReport.objects.select_related("reporter", "reviewed_by"), pk=pk)

    if request.method == "POST":
        if report.reporter_id == request.user.id:
            messages.error(request, "You cannot review your own report.")
            return redirect("review_report", pk=pk)

        action = request.POST.get("action")
        if action == "verify":
            report.status = ScamReport.Status.VERIFIED
            report.rejection_reason = ""
        elif action == "reject":
            reason = request.POST.get("rejection_reason", "").strip()
            if not reason:
                messages.error(request, "Please give a reason for rejecting this report.")
                return redirect("review_report", pk=pk)
            report.status = ScamReport.Status.REJECTED
            report.rejection_reason = reason[:500]
        else:
            return HttpResponseBadRequest("Unknown action.")

        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()
        messages.success(request, f"Report marked as {report.get_status_display().lower()}.")
        return redirect("moderation_queue")

    related = ScamReport.objects.filter(
        indicator_type=report.indicator_type,
        normalized_value=report.normalized_value,
    ).exclude(pk=report.pk)
    return render(request, "reports/review.html", {"report": report, "related": related})