# Smart Job Portal (Django)

A full stack job portal with **smart resume matching**.

## Features
- Role based login: **Candidate**, **Recruiter**, **Admin**
- Recruiters: post / edit / delete jobs, view applicants **ranked by match score**, shortlist or reject
- Candidates: search jobs (keyword, location, type), upload resume (PDF/TXT), get an instant **match score** with matched and missing skills
- Admin: analytics dashboard (Chart.js) + Django admin panel
- Docker + PostgreSQL support

## How the matching works (`jobs/matching.py`)
Score (0-100) = **60% skill coverage** + **40% TF-IDF cosine similarity**
1. Skill coverage: required skills of the job found in the resume text.
2. TF-IDF + cosine similarity (scikit-learn) between the job text and the resume text.

## Run locally
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt

python manage.py makemigrations accounts jobs
python manage.py migrate
python manage.py seed_demo      # demo users + sample jobs (optional)
python manage.py runserver
```
Open http://127.0.0.1:8000

Demo logins (from `seed_demo`):
| Role | Username | Password |
|---|---|---|
| Admin | admin | admin12345 |
| Recruiter | recruiter1 | recruiter12345 |
| Candidate | candidate1 | candidate12345 |

(Without seed data, create your own admin: `python manage.py createsuperuser`.)

## Run with Docker (PostgreSQL)
```bash
docker compose up --build
# in another terminal:
docker compose exec web python manage.py seed_demo
```

## Deploy (Render.com, free tier)
1. Push this folder to GitHub.
2. Render > New > Web Service > connect repo, Runtime: **Docker**.
3. Environment variables: `DEBUG=0`, `SECRET_KEY=<random string>`, `ALLOWED_HOSTS=<your-app>.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://<your-app>.onrender.com`
4. After deploy open the Shell tab: `python manage.py seed_demo` (or `createsuperuser`).
Note: free tier uses SQLite and loses data/uploads on restart. Add a Render PostgreSQL database and set the `POSTGRES_*` variables for permanent data. Uploaded resumes need a persistent disk or S3 for production.

## Project structure
```
config/     settings, urls
accounts/   custom User (role), register / login
jobs/       models, views, matching.py (ML), forms, seed command
templates/  HTML (Bootstrap 5)
static/css/ styling
```

## Ideas to make it yours (add 1-2 before interviews)
- Email notification when status changes
- Show resume skill gaps with course suggestions
- Replace TF-IDF with sentence-transformers embeddings
- Saved jobs / bookmarks
- Unit tests for `compute_match`
