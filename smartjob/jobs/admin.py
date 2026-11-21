from django.contrib import admin

from .models import Application, Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "job_type", "recruiter", "is_active", "created_at")
    list_filter = ("job_type", "is_active")
    search_fields = ("title", "company", "skills")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "match_score", "status", "applied_at")
    list_filter = ("status",)
