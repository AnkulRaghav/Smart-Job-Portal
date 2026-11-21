from django.conf import settings
from django.db import models
from django.urls import reverse


class Job(models.Model):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    REMOTE = "remote"
    TYPE_CHOICES = [
        (FULL_TIME, "Full time"),
        (PART_TIME, "Part time"),
        (INTERNSHIP, "Internship"),
        (REMOTE, "Remote"),
    ]

    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=FULL_TIME)
    salary = models.CharField(max_length=80, blank=True, help_text="e.g. 4-6 LPA")
    skills = models.CharField(
        max_length=300,
        help_text="Comma separated required skills, e.g. python, django, sql, git",
    )
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}"

    def get_absolute_url(self):
        return reverse("job_detail", args=[self.pk])

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]


class Application(models.Model):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    STATUS_CHOICES = [
        (APPLIED, "Applied"),
        (SHORTLISTED, "Shortlisted"),
        (REJECTED, "Rejected"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to="resumes/")
    cover_note = models.TextField(blank=True)
    resume_text = models.TextField(blank=True, editable=False)
    match_score = models.FloatField(default=0)
    matched_skills = models.CharField(max_length=300, blank=True)
    missing_skills = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=APPLIED)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-match_score", "-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["job", "candidate"], name="one_application_per_job"),
        ]

    def __str__(self):
        return f"{self.candidate} -> {self.job}"

    @property
    def matched_list(self):
        return [s for s in self.matched_skills.split(",") if s]

    @property
    def missing_list(self):
        return [s for s in self.missing_skills.split(",") if s]
