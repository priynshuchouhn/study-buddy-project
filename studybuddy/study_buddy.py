# studybuddy/studybuddy.py
"""
Utility helpers for StudyBuddy workflow.
"""

from .skill_extractor import extract_text_from_resume, extract_skills_from_text, extract_email_from_text
from .quiz_generator import generate_quiz_questions, evaluate_quiz_answers
from .matching import match_partner_smart

class StudyBuddyUtils:
    """
    Small helper wrapper used by higher-level code if you prefer object API.
    """

    def extract_resume_and_skills(self, resume_path: str):
        text = extract_text_from_resume(resume_path)
        skills = extract_skills_from_text(text)
        email = extract_email_from_text(text)
        return {"text": text, "skills": skills, "email": email}

    def make_quiz(self, skills, num_questions: int = 5):
        return generate_quiz_questions(skills, num_questions=num_questions)

    def evaluate(self, questions, user_answers):
        return evaluate_quiz_answers(questions, user_answers)

    def find_partner(self, score: int, skills, email: str = None):
        return match_partner_smart(score=score, user_skills=skills, user_email=email)
