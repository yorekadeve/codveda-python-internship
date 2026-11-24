from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ScamReportForm
from .models import ScamReport
from .utils import detect_indicator, lookup_values


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
    if report.reporter != request.user and not request.user.is_staff:
        raise Http404
    if not report.evidence:
        raise Http404
    return FileResponse(report.evidence.open("rb"))

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