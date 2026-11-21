from django.urls import path

from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("go/", views.go, name="go"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/apply/", views.apply, name="apply"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("recruiter/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("recruiter/jobs/new/", views.job_create, name="job_create"),
    path("recruiter/jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("recruiter/jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("recruiter/jobs/<int:pk>/applicants/", views.job_applicants, name="job_applicants"),
    path("analytics/", views.analytics, name="analytics"),
]
