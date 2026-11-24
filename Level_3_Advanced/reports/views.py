from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Max
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from audit.throttle import rate_limit
from audit.utils import log_event

from .forms import ScamReportForm
from .models import Corroboration, ScamReport
from .stats import detailed_stats
from .utils import detect_indicator, lookup_values

REVIEW_PERMISSION = "reports.review_reports"


@rate_limit("search", 30, 60)
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
            active = reports.exclude(status=ScamReport.Status.REJECTED)
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
            context["confirmations"] = Corroboration.objects.filter(report__in=active).count()

            target = active.order_by("created_at").first()
            context["confirm_target"] = target
            if target and request.user.is_authenticated:
                already = Corroboration.objects.filter(
                    report=target, user=request.user
                ).exists()
                context["already_confirmed"] = already
                context["can_confirm"] = target.reporter_id != request.user.id and not already

    return render(request, "reports/check.html", context)


@login_required
@rate_limit("confirm", 20, 3600, methods=("POST",))
@require_POST
def confirm_report(request, pk):
    report = get_object_or_404(
        ScamReport.objects.exclude(status=ScamReport.Status.REJECTED), pk=pk
    )
    if report.reporter_id == request.user.id:
        messages.error(request, "You cannot confirm your own report.")
    else:
        _, created = Corroboration.objects.get_or_create(report=report, user=request.user)
        if created:
            log_event("report_confirmed", request=request, target=f"report:{report.pk}")
            messages.success(request, "Thank you. Your confirmation was added.")
        else:
            messages.info(request, "You have already confirmed this.")

    query = urlencode({"q": report.indicator_value})
    return redirect(f"{reverse('check_scam')}?{query}")


@rate_limit("stats", 60, 60)
def statistics(request):
    return render(request, "reports/stats.html", detailed_stats())


@login_required
@rate_limit("submit_report", 10, 3600, methods=("POST",))
def submit_report(request):
    if request.method == "POST":
        form = ScamReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            log_event("report_submitted", request=request, target=f"report:{report.pk}")
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
    is_owner = report.reporter == request.user
    if not is_owner and not request.user.has_perm(REVIEW_PERMISSION):
        raise Http404
    if not report.evidence:
        raise Http404
    if not is_owner:
        log_event("evidence_viewed", request=request, target=f"report:{report.pk}")
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
        .annotate(confirmations=Count("corroborations"))
        .order_by("-confirmations", "created_at")
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
    report = get_object_or_404(
        ScamReport.objects.select_related("reporter", "reviewed_by"), pk=pk
    )

    if request.method == "POST":
        if report.reporter_id == request.user.id:
            messages.error(request, "You cannot review your own report.")
            return redirect("review_report", pk=pk)

        action = request.POST.get("action")
        if action == "verify":
            report.status = ScamReport.Status.VERIFIED
            report.rejection_reason = ""
            details = ""
        elif action == "reject":
            reason = request.POST.get("rejection_reason", "").strip()
            if not reason:
                messages.error(request, "Please give a reason for rejecting this report.")
                return redirect("review_report", pk=pk)
            report.status = ScamReport.Status.REJECTED
            report.rejection_reason = reason[:500]
            details = f"reason: {report.rejection_reason}"
        else:
            return HttpResponseBadRequest("Unknown action.")

        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()
        log_event(
            f"report_{report.status}",
            request=request,
            target=f"report:{report.pk}",
            details=details,
        )
        messages.success(request, f"Report marked as {report.get_status_display().lower()}.")
        return redirect("moderation_queue")

    related = ScamReport.objects.filter(
        indicator_type=report.indicator_type,
        normalized_value=report.normalized_value,
    ).exclude(pk=report.pk)
    return render(request, "reports/review.html", {"report": report, "related": related})