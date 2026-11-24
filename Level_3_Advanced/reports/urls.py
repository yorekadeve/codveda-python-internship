from django.urls import path

from . import views

urlpatterns = [
    path("check/", views.check_scam, name="check_scam"),
    path("report/new/", views.submit_report, name="submit_report"),
    path("my-reports/", views.my_reports, name="my_reports"),
    path("my-reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("my-reports/<int:pk>/evidence/", views.evidence_file, name="evidence_file"),
]