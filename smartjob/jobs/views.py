from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User

from .decorators import role_required
from .forms import ApplicationForm, JobForm, StatusForm
from .matching import compute_match, extract_text
from .models import Application, Job


# ---------- public ----------
def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related("recruiter")
    q = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    job_type = request.GET.get("job_type", "")

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) | Q(company__icontains=q) | Q(skills__icontains=q) | Q(description__icontains=q)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    page = Paginator(jobs, 6).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "jobs/job_list.html",
        {"page": page, "types": Job.TYPE_CHOICES, "q": q, "location": location,
         "job_type": job_type, "querystring": params.urlencode()},
    )


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if not job.is_active and not (request.user.is_authenticated and request.user == job.recruiter):
        return redirect("job_list")
    application = None
    if request.user.is_authenticated and request.user.is_candidate:
        application = Application.objects.filter(job=job, candidate=request.user).first()
    return render(request, "jobs/job_detail.html", {"job": job, "application": application})


@login_required
def go(request):
    """Send each role to its own home page after login."""
    user = request.user
    if user.is_portal_admin:
        return redirect("analytics")
    if user.is_recruiter:
        return redirect("recruiter_dashboard")
    return redirect("my_applications")


# ---------- candidate ----------
@role_required(User.CANDIDATE)
def apply(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect("my_applications")

    form = ApplicationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.candidate = request.user
        text = extract_text(application.resume)
        application.resume_text = text
        score, matched, missing = compute_match(text, job)
        application.match_score = score
        application.matched_skills = ",".join(matched)
        application.missing_skills = ",".join(missing)
        application.save()
        messages.success(request, f"Application sent! Your resume match score is {score}%.")
        return redirect("my_applications")
    return render(request, "jobs/apply.html", {"job": job, "form": form})


@role_required(User.CANDIDATE)
def my_applications(request):
    applications = Application.objects.filter(candidate=request.user).select_related("job")
    return render(request, "jobs/my_applications.html", {"applications": applications})


# ---------- recruiter ----------
@role_required(User.RECRUITER)
def recruiter_dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user).annotate(
        total=Count("applications"),
        shortlisted=Count("applications", filter=Q(applications__status=Application.SHORTLISTED)),
        avg_score=Avg("applications__match_score"),
    )
    return render(request, "jobs/recruiter_dashboard.html", {"jobs": jobs})


@role_required(User.RECRUITER)
def job_create(request):
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user
        job.save()
        messages.success(request, "Job posted.")
        return redirect("recruiter_dashboard")
    return render(request, "jobs/job_form.html", {"form": form, "title": "Post a new job"})


@role_required(User.RECRUITER)
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    form = JobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Job updated.")
        return redirect("recruiter_dashboard")
    return render(request, "jobs/job_form.html", {"form": form, "title": "Edit job"})


@role_required(User.RECRUITER)
@require_POST
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    job.delete()
    messages.success(request, "Job deleted.")
    return redirect("recruiter_dashboard")


@role_required(User.RECRUITER)
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.method == "POST":
        form = StatusForm(request.POST)
        if form.is_valid():
            application = get_object_or_404(Application, pk=form.cleaned_data["application_id"], job=job)
            application.status = form.cleaned_data["status"]
            application.save(update_fields=["status"])
            messages.success(request, f"{application.candidate.username} marked as {application.get_status_display()}.")
        return redirect("job_applicants", pk=job.pk)
    applications = job.applications.select_related("candidate")  # already ordered by best match
    return render(request, "jobs/applicants.html", {"job": job, "applications": applications})


# ---------- admin analytics ----------
@role_required(User.ADMIN)
def analytics(request):
    apps = Application.objects.all()
    by_month = (
        apps.annotate(m=TruncMonth("applied_at")).values("m").annotate(c=Count("id")).order_by("m")
    )
    top_jobs = Job.objects.annotate(c=Count("applications")).order_by("-c")[:5]
    type_counts = Job.objects.values("job_type").annotate(c=Count("id"))
    status_counts = apps.values("status").annotate(c=Count("id"))
    type_labels = dict(Job.TYPE_CHOICES)
    status_labels = dict(Application.STATUS_CHOICES)

    charts = {
        "months": {"labels": [r["m"].strftime("%b %Y") for r in by_month], "data": [r["c"] for r in by_month]},
        "top_jobs": {"labels": [j.title for j in top_jobs], "data": [j.c for j in top_jobs]},
        "types": {"labels": [type_labels[r["job_type"]] for r in type_counts], "data": [r["c"] for r in type_counts]},
        "status": {"labels": [status_labels[r["status"]] for r in status_counts], "data": [r["c"] for r in status_counts]},
    }
    stats = {
        "candidates": User.objects.filter(role=User.CANDIDATE).count(),
        "recruiters": User.objects.filter(role=User.RECRUITER).count(),
        "jobs": Job.objects.count(),
        "applications": apps.count(),
        "avg_score": round(apps.aggregate(a=Avg("match_score"))["a"] or 0, 1),
    }
    return render(request, "jobs/analytics.html", {"stats": stats, "charts": charts})
