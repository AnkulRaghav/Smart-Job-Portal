# Interview Guide + Resume Points

## Resume entry
**Smart Job Portal** | Django, PostgreSQL, scikit-learn, Bootstrap, Docker | GitHub: <link> | Live: <link>
- Built a role-based (candidate / recruiter / admin) job portal with Django authentication and authorization
- Implemented resume-job matching using TF-IDF + cosine similarity combined with skill coverage scoring; recruiters see applicants ranked by fit
- Designed relational schema (User, Job, Application) with unique constraints, search/filter and pagination
- Created admin analytics dashboard with Chart.js and containerized the app with Docker + PostgreSQL

## Questions you will be asked
**1. How does the matching work?**
Resume text is extracted (pypdf). Score = 60% skill coverage (required skills found in resume) + 40% text similarity. For similarity I convert job and resume to TF-IDF vectors and take cosine similarity. TF-IDF gives rare, meaningful words more weight than common ones.

**2. Why TF-IDF and not deep learning?**
It is fast, needs no training data, runs on a free server and is explainable. Limitation: it misses synonyms ("ML" vs "machine learning"). Next step would be sentence-transformer embeddings.

**3. How did you handle roles and security?**
Custom User model with a `role` field, a `role_required` decorator (403 for wrong role), CSRF tokens on all forms, recruiters can only access their own jobs (`get_object_or_404(..., recruiter=request.user)`), file type and size validation on resume upload.

**4. How do you prevent duplicate applications?**
A database `UniqueConstraint` on (job, candidate) plus a check in the view.

**5. What is the N+1 query problem? Where did you avoid it?**
Looping over objects triggers one query each. I used `select_related` (job list, applications) and `annotate(Count/Avg)` in the recruiter dashboard.

**6. Why a custom User model?**
Django recommends it at project start so you can add fields (role) without painful migrations later.

**7. What would you improve?**
Email notifications, async resume parsing (Celery), embeddings for matching, S3 for file storage, automated tests.

## Tip
Run the project, click through every page, then read `jobs/views.py` and `jobs/matching.py` line by line until you can explain them without looking.
