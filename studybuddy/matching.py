# studybuddy/matching.py
"""
Partner matching logic for StudyBuddy.
Exposes match_partner_smart(score, user_skills, user_email)
"""

from typing import List, Dict

# optional vector similarity with sklearn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAVE_SKLEARN = True
except Exception:
    _HAVE_SKLEARN = False

# sample partners (replace with CSV/database in future)
SAMPLE_PARTNERS = [
    {"name": "Aarav Mehta", "email": "aarav@cmrit.ac.in", "skills": ["Python", "Flask", "SQL"], "score": 4, "bio": "Backend dev"},
    {"name": "Neha Gupta", "email": "neha@cmrit.ac.in", "skills": ["Data Analysis", "Pandas", "NumPy"], "score": 3, "bio": "Data analyst"},
    {"name": "Rohit Sharma", "email": "rohit@cmrit.ac.in", "skills": ["Machine Learning", "TensorFlow", "PyTorch"], "score": 5, "bio": "ML engineer"},
    {"name": "Sana Rao", "email": "sana@cmrit.ac.in", "skills": ["React", "HTML", "CSS"], "score": 2, "bio": "Frontend dev"},
    {"name": "Kabir Singh", "email": "kabir@cmrit.ac.in", "skills": ["Java", "Spring Boot", "REST"], "score": 4, "bio": "Microservices enthusiast"},
    {"name": "Isha Verma", "email": "isha@cmrit.ac.in", "skills": ["C++", "Data Structures", "Algorithms"], "score": 5, "bio": "Competitive programmer"},
    {"name": "Dev Patel", "email": "dev@cmrit.ac.in", "skills": ["AWS", "Docker", "CI/CD"], "score": 4, "bio": "DevOps engineer"},
    {"name": "Maya Nair", "email": "maya@cmrit.ac.in", "skills": ["Cybersecurity", "Networking", "Linux"], "score": 3, "bio": "Security learner"},
    {"name": "Anuj Kulkarni", "email": "anuj@cmrit.ac.in", "skills": ["Android", "Kotlin", "Firebase"], "score": 2, "bio": "Mobile app dev"},
    {"name": "Rhea D'Souza", "email": "rhea@cmrit.ac.in", "skills": ["UI/UX", "Figma", "Accessibility"], "score": 3, "bio": "Design focused"},
    {"name": "Tanishq Rao", "email": "tanishq@cmrit.ac.in", "skills": ["Go", "Concurrency", "APIs"], "score": 4, "bio": "Systems programmer"},
    {"name": "Vikram Jain", "email": "vikram@cmrit.ac.in", "skills": ["Rust", "Systems", "WASM"], "score": 5, "bio": "Low-level tinkerer"},
    {"name": "Bhavya Shah", "email": "bhavya@cmrit.ac.in", "skills": ["Blockchain", "Solidity", "Smart Contracts"], "score": 3, "bio": "Web3 explorer"},
    {"name": "Simran Kaur", "email": "simran@cmrit.ac.in", "skills": ["Django", "PostgreSQL", "HTML"], "score": 4, "bio": "Fullstack python"},
    {"name": "Yash Malhotra", "email": "yash@cmrit.ac.in", "skills": ["Data Science", "Scikit-Learn", "Matplotlib"], "score": 3, "bio": "Model builder"},
    {"name": "Pooja Reddy", "email": "pooja@cmrit.ac.in", "skills": ["TensorFlow", "Computer Vision", "OpenCV"], "score": 5, "bio": "CV specialist"},
    {"name": "Harshita Agarwal", "email": "harshita@cmrit.ac.in", "skills": ["React", "TypeScript", "Redux"], "score": 3, "bio": "Frontend engineer"},
    {"name": "Nikhil Bhat", "email": "nikhil@cmrit.ac.in", "skills": ["MongoDB", "Express", "Node.js"], "score": 2, "bio": "Learning MERN stack"},
    {"name": "Tanvi Deshpande", "email": "tanvi@cmrit.ac.in", "skills": ["Azure", "Kubernetes", "Helm"], "score": 4, "bio": "Cloud native"},
    {"name": "Pranav Iyer", "email": "pranav@cmrit.ac.in", "skills": ["Game Dev", "Unity", "C#"], "score": 2, "bio": "Indie game dev"},
    {"name": "Zara Hussain", "email": "zara@cmrit.ac.in", "skills": ["NLP", "Transformers", "SpaCy"], "score": 5, "bio": "Language model enthusiast"},
    {"name": "Omkar Joshi", "email": "omkar@cmrit.ac.in", "skills": ["Embedded", "C", "Arduino"], "score": 3, "bio": "Hardware hacker"}
]


def _set_overlap_score(a: List[str], b: List[str]) -> float:
    sa = set([x.lower() for x in a])
    sb = set([x.lower() for x in b])
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def _tfidf_similarity(a: List[str], b: List[str]) -> float:
    try:
        docs = [" ".join(a), " ".join(b)]
        vec = TfidfVectorizer().fit_transform(docs)
        sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
        return float(sim)
    except Exception:
        return _set_overlap_score(a, b)


def match_partner_smart(score: int, user_skills: List[str], user_email: str = None) -> Dict:
    """
    Return best partner dict (name, email, shared_skill, bio).
    Heuristics:
      - compute similarity between user_skills and each candidate
      - prefer candidates with slightly higher score (if user is intermediate/advanced)
      - avoid matching with self (by email)
    """
    if not user_skills:
        # fallback: return first partner
        return SAMPLE_PARTNERS[0]

    scored = []
    for cand in SAMPLE_PARTNERS:
        if user_email and cand.get("email", "").lower() == user_email.lower():
            continue
        if _HAVE_SKLEARN:
            sim = _tfidf_similarity(user_skills, cand.get("skills", []))
        else:
            sim = _set_overlap_score(user_skills, cand.get("skills", []))

        # boost for candidates with score >= user score when user is advanced
        bonus = 0.0
        try:
            if score >= 4 and cand.get("score", 0) >= 4:
                bonus = 0.12
        except Exception:
            bonus = 0.0

        final_score = sim + bonus
        scored.append((final_score, cand))

    if not scored:
        return {"name": "No match", "email": "", "shared_skill": None, "bio": ""}

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0][1]

    # find best shared skill or pick first skill
    shared = None
    uset = set(s.lower() for s in user_skills)
    for s in top.get("skills", []):
        if s.lower() in uset:
            shared = s
            break

    return {
        "name": top.get("name"),
        "email": top.get("email"),
        "shared_skill": shared or (top.get("skills")[0] if top.get("skills") else None),
        "bio": top.get("bio", "")
    }
