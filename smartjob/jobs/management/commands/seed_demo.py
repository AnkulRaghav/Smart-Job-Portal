from django.core.management.base import BaseCommand

from accounts.models import User
from jobs.models import Job

JOBS = [
    ("Python Django Developer", "TechNova", "Noida", "full_time", "4-6 LPA", "python, django, rest api, sql, git",
     "Build and maintain REST APIs using Django and PostgreSQL. Work with the frontend team, write tests and deploy with Docker."),
    ("React Frontend Developer", "PixelWorks", "Delhi", "full_time", "4-7 LPA", "react, javascript, html, css, git",
     "Create responsive user interfaces with React. Integrate REST APIs, manage state and write clean reusable components."),
    ("Data Analyst", "InsightLabs", "Gurugram", "full_time", "3-5 LPA", "sql, python, excel, power bi, pandas",
     "Analyse business data, build dashboards in Power BI and share insights with stakeholders using SQL and Pandas."),
    ("Machine Learning Intern", "AIQuest", "Remote", "internship", "15-20k / month", "python, scikit-learn, pandas, numpy, nlp",
     "Assist in building NLP and classification models. Clean datasets, train models and evaluate results."),
    ("Full Stack Developer (MERN)", "CloudNest", "Bengaluru", "remote", "6-9 LPA", "react, node.js, express, mongodb, javascript",
     "Develop full stack web apps with the MERN stack, design REST APIs and deploy to the cloud."),
    ("DevOps Engineer (Fresher)", "InfraOps", "Pune", "full_time", "4-6 LPA", "docker, linux, git, aws, ci/cd",
     "Containerise applications, build CI/CD pipelines with GitHub Actions and deploy to AWS."),
]


class Command(BaseCommand):
    help = "Create demo users and sample jobs"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")
        rec, created = User.objects.get_or_create(
            username="recruiter1", defaults={"email": "rec@example.com", "role": User.RECRUITER})
        if created:
            rec.set_password("recruiter12345")
            rec.save()
        cand, created = User.objects.get_or_create(
            username="candidate1", defaults={"email": "cand@example.com", "role": User.CANDIDATE})
        if created:
            cand.set_password("candidate12345")
            cand.save()

        for title, company, loc, jtype, salary, skills, desc in JOBS:
            Job.objects.get_or_create(
                title=title, company=company,
                defaults=dict(recruiter=rec, location=loc, job_type=jtype, salary=salary, skills=skills, description=desc),
            )
        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Logins: admin/admin12345, recruiter1/recruiter12345, candidate1/candidate12345"))
