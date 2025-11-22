# studybuddy/skill_extractor.py
import re

_old_extract_text = None
_old_extract_skills = None
_old_extract_name = None

try:
    from resume_skill_quiz.extractor import (
        extract_text_from_resume as _old_extract_text,
        extract_skills as _old_extract_skills,
        extract_name as _old_extract_name
    )
except Exception as e:
    print("[studybuddy.skill_extractor] Warning: could not import old extractor:", e)

EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', flags=re.IGNORECASE)


def extract_text_from_resume(path: str) -> str:
    """Extract text from resume (PDF or DOCX)."""
    if _old_extract_text:
        try:
            return _old_extract_text(path) or ""
        except Exception as e:
            print("[skill_extractor] old extractor failed:", e)

    # fallback PDF extraction
    if path.lower().endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            pages = [(p.extract_text() or "") for p in reader.pages]
            return " ".join(pages)
        except Exception as e:
            print("[skill_extractor] fallback PDF extraction failed:", e)

    # fallback DOCX extraction
    if path.lower().endswith(".docx"):
        try:
            import docx
            doc = docx.Document(path)
            return " ".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print("[skill_extractor] DOCX extraction failed:", e)

    return ""


def extract_skills_from_text(text: str):
    """Extract skills from resume text using keyword matching."""
    if _old_extract_skills:
        try:
            return _old_extract_skills(text) or []
        except Exception as e:
            print("[skill_extractor] old extract_skills failed:", e)

    keywords = [
        "python", "java", "sql", "flask", "django", "react", "angular", "vue",
        "machine learning", "deep learning", "data analysis", "pandas", "numpy",
        "matplotlib", "seaborn", "sklearn"
    ]
    text_l = text.lower()
    return [k for k in keywords if k in text_l]


def extract_email_from_text(text: str):
    """Extract first email found in text."""
    if not text:
        return None
    m = EMAIL_PATTERN.search(text)
    return m.group(0).lower().strip() if m else None


print("[INFO] studybuddy.skill_extractor loaded successfully")
