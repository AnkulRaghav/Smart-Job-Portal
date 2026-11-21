from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (CANDIDATE, "Candidate (job seeker)"),
        (RECRUITER, "Recruiter (hiring)"),
        (ADMIN, "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CANDIDATE)

    def save(self, *args, **kwargs):
        # users made with createsuperuser automatically become portal admins
        if self.is_superuser:
            self.role = self.ADMIN
        super().save(*args, **kwargs)

    @property
    def is_candidate(self):
        return self.role == self.CANDIDATE

    @property
    def is_recruiter(self):
        return self.role == self.RECRUITER

    @property
    def is_portal_admin(self):
        return self.role == self.ADMIN
