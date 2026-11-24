from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ScamReportForm
from .models import ScamReport


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