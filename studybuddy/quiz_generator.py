# studybuddy/quiz_generator.py
"""
Quiz wrapper for StudyBuddy that reuses studybuddy.mistral_api.
Exposes:
 - generate_quiz_questions(skills, num_questions=5)
 - evaluate_quiz_answers(questions, user_answers)
"""

import json
import traceback

# ✅ Use relative import for reliability
try:
    from .mistral_api import generate_quiz as _mistral_generate, get_explanation as _mistral_explain
    _HAVE_MISTRAL = True
except Exception as e:
    _mistral_generate = None
    _mistral_explain = None
    _HAVE_MISTRAL = False
    print("[studybuddy.quiz] Warning: could not import mistral_api:", e)


def _normalize_questions(obj):
    """Normalize quiz output into a clean list of dicts."""
    if isinstance(obj, list):
        return [q for q in obj if isinstance(q, dict) and "question" in q and "options" in q and "answer" in q]

    if isinstance(obj, dict) and "quiz" in obj:
        return _normalize_questions(obj["quiz"])

    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            return _normalize_questions(parsed)
        except Exception:
            return []

    return []


def generate_quiz_questions(skills, num_questions=5):
    """Generate quiz questions using Mistral API."""
    if not skills:
        return []

    if not _HAVE_MISTRAL:
        print("[studybuddy.quiz] No mistral_api available.")
        return []

    try:
        raw = _mistral_generate(skills)
        questions = _normalize_questions(raw)
        return questions[:num_questions]
    except Exception as e:
        print("[studybuddy.quiz] Error generating quiz:", e)
        traceback.print_exc()
        return []


def evaluate_quiz_answers(questions, user_answers):
    """Evaluate user answers against correct answers."""
    score = 0
    total = len(questions)
    results = []

    for i, q in enumerate(questions):
        correct = str(q.get("answer", "")).strip().upper()
        user_ans = (user_answers[i] or "").strip().upper() if i < len(user_answers) else ""
        is_correct = (user_ans == correct)

        if is_correct:
            score += 1

        explanation = q.get("explanation") or ""

        if not is_correct and not explanation and _HAVE_MISTRAL and _mistral_explain:
            try:
                explanation = _mistral_explain(q.get("question", ""), user_ans, correct)
            except Exception:
                explanation = ""

        results.append({
            "question": q.get("question"),
            "user_answer": user_ans,
            "correct_answer": correct,
            "explanation": explanation,
            "is_correct": is_correct,
            "skill": q.get("skill", "")
        })

    return score, total, results
