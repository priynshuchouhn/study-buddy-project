# resume_skill_quiz/extractor.py
import re
from PyPDF2 import PdfReader

# docx2txt is optional; we attempt to import it but don't fail if not present.
try:
    import docx2txt
except Exception:
    docx2txt = None

SKILLS_DB = [
    "Python", "Java", "Machine Learning", "SQL", "C++", "HTML", "CSS", "JavaScript",
    "Bootstrap", "Tailwind", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Flask", "Django",
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Scikit-learn", "TensorFlow", "Keras", "PyTorch", "Data Analysis", "Data Visualization", "Deep Learning",
    "Artificial Intelligence", "Natural Language Processing", "Git", "GitHub", "Docker", "AWS", "Google Cloud",
    "Azure", "Jira", "VS Code", "Jupyter", "Linux", "Power BI", "Tableau", "OOP", "DSA", "REST API",
    "Microservices", "Agile", "CI/CD", "Unit Testing", "Cloud Computing", "Communication", "Leadership",
    "Teamwork", "Problem Solving", "Time Management", "Creativity", "Critical Thinking"
]


def extract_text_from_resume(file_path: str) -> str:
    """
    Extract text from a .pdf or .docx resume.
    Returns an empty string if extraction fails or file type unsupported.
    """
    if not file_path:
        return ""

    file_path_lower = file_path.lower()
    try:
        if file_path_lower.endswith(".pdf"):
            reader = PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    pages_text.append(txt)
            return " ".join(pages_text)
        elif file_path_lower.endswith(".docx"):
            if docx2txt is None:
                raise RuntimeError("docx2txt not installed; cannot extract .docx files")
            return docx2txt.process(file_path) or ""
        else:
            # not supported type
            return ""
    except Exception as e:
        # Do not raise here; return empty string so caller can show friendly error.
        print(f"[extractor] Error extracting text from {file_path}: {e}")
        return ""


def extract_skills(text: str):
    """
    Return a list of skills found in the provided text (case-insensitive).
    The returned list preserves the SKILLS_DB order and uniqueness.
    """
    if not text:
        return []

    lower = text.lower()
    found = []
    seen = set()
    for skill in SKILLS_DB:
        if skill.lower() in lower and skill not in seen:
            found.append(skill)
            seen.add(skill)
    return found


def extract_name(text: str):
    """
    Try to extract a full name using a simple regex pattern.
    If not found, returns 'Unknown'.
    """
    if not text:
        return "Unknown"
    match = re.search(r'(?i)(?:name[:\-]?\s*)([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})', text)

    return match.group(1) if match else "Unknown"


def extract_email(text: str):
    """
    Find the first email address in the text (simple regex).
    Returns the email string in lowercase or None if not found.
    """
    if not text:
        return None
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0).strip().lower() if match else None
