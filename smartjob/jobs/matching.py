"""
Resume <-> Job matching engine.

Final score (0-100) = 60% skill coverage + 40% text similarity

1. Skill coverage : how many of the job's required skills appear in the resume.
2. Text similarity: TF-IDF vectors of (job text, resume text) compared with
                    cosine similarity (scikit-learn).
"""
import re
from io import BytesIO

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_WEIGHT = 0.6
TEXT_WEIGHT = 0.4


def extract_text(uploaded_file):
    """Return plain text from an uploaded PDF or TXT file."""
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    uploaded_file.seek(0)

    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return data.decode("utf-8", errors="ignore")


def _skill_in_text(skill, text):
    pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
    return re.search(pattern, text) is not None


def compute_match(resume_text, job):
    """Return (score, matched_skills, missing_skills) for a resume against a Job."""
    resume_l = (resume_text or "").lower()
    if not resume_l.strip():
        return 0.0, [], [s.lower() for s in job.skill_list]

    skills = [s.lower() for s in job.skill_list]
    matched = [s for s in skills if _skill_in_text(s, resume_l)]
    missing = [s for s in skills if s not in matched]

    job_doc = f"{job.title} {job.description} {job.skills}"
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        tfidf = vectorizer.fit_transform([job_doc, resume_l])
        similarity = float(cosine_similarity(tfidf[0], tfidf[1])[0][0])
    except ValueError:  # empty vocabulary
        similarity = 0.0

    # raw cosine values for relevant resumes sit around 0.1-0.35, so scale up
    text_score = min(similarity * 3, 1.0) * 100

    if skills:
        skill_score = len(matched) / len(skills) * 100
        score = SKILL_WEIGHT * skill_score + TEXT_WEIGHT * text_score
    else:
        score = text_score
    return round(score, 1), matched, missing
