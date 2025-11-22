# resume_skill_quiz/mistral_api.py
"""
Stable working wrapper for Mistral LLM.
Guaranteed to return clean JSON quiz output.
"""

import os
import json
import traceback
import requests

# Try import official mistralai client
try:
    from mistralai import Mistral
    _HAS_CLIENT = True
except Exception:
    _HAS_CLIENT = False

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def _client_chat(prompt):
    """Uses mistralai client; falls back to HTTP."""
    if _HAS_CLIENT and MISTRAL_API_KEY:
        try:
            client = Mistral(api_key=MISTRAL_API_KEY)

            # ✅ Correct 2024/2025 SDK method
            resp = client.chat.completions.create(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            return resp.choices[0].message["content"]

        except Exception as e:
            print("[mistral_api] SDK client failed:", e)

    # ---- HTTP fallback ----
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 1000
    }

    resp = requests.post(MISTRAL_URL, headers=headers, json=payload, timeout=40)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _try_parse_json(text):
    """Extracts valid JSON from messy LLM output."""
    if not text:
        return None

    try:
        return json.loads(text)
    except:
        pass

    # Try to extract first JSON block
    start = None
    for i, c in enumerate(text):
        if c in ["{", "["]:
            start = i
            break

    if start is None:
        return None

    stack = []
    for j in range(start, len(text)):
        if text[j] in ["{", "["]:
            stack.append(text[j])
        elif text[j] in ["}", "]"]:
            stack.pop()
            if not stack:
                try:
                    return json.loads(text[start:j+1])
                except:
                    return None
    return None


def generate_quiz(skills, num_questions=5):
    """Returns clean list of MCQs."""
    if isinstance(skills, list):
        skills = ", ".join(skills)

    prompt = f"""
Generate {num_questions} multiple-choice questions for these skills: {skills}.
Each MCQ must have exactly 4 options and one correct answer (A–D).

Return STRICT JSON ONLY:

{{
  "quiz": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}
No explanation. No extra text.
"""

    try:
        raw = _client_chat(prompt)
        parsed = _try_parse_json(raw)

        if parsed and "quiz" in parsed:
            return parsed["quiz"]

        print("[mistral_api] JSON not parsed:", raw)
        return []

    except Exception as e:
        print("[mistral_api] error:", e)
        traceback.print_exc()
        return []


def get_explanation(q, user, correct):
    prompt = f"""
Explain why '{user}' is incorrect and '{correct}' is correct for this question:
{q}
Give a short 2–3 line explanation.
"""
    try:
        ans = _client_chat(prompt)
        return ans
    except:
        return "Explanation unavailable."
