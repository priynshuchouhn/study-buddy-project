"""
resume_skill_quiz package init

Exports:
  - extract_text_from_resume
  - extract_skills
  - extract_name
  - extract_email
  - generate_quiz
  - get_explanation
"""

from .extractor import extract_text_from_resume, extract_skills, extract_name, extract_email

# Import Mistral helpers from the `studybuddy` package if available.
# Use absolute import and guard so package import doesn't fail when running
# the app as a top-level script or in environments where package layout
# differs.
try:
    from studybuddy.mistral_api import generate_quiz, get_explanation
except Exception:
    generate_quiz = None
    get_explanation = None

__all__ = [
    "extract_text_from_resume",
    "extract_skills",
    "extract_name",
    "extract_email",
    "generate_quiz",
    "get_explanation",
]
