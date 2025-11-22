import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime

# StudyBuddy package imports
from studybuddy.skill_extractor import (
    extract_text_from_resume,
    extract_skills_from_text,
    extract_email_from_text
)
from studybuddy.quiz_generator import generate_quiz_questions, evaluate_quiz_answers
from studybuddy.matching import match_partner_smart
# ❌ Removed invalid import: call_mistral_for_skill
# If you need direct Mistral helpers, use:
# from studybuddy.mistral_api import generate_quiz, get_explanation

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------------------------------
# 1️⃣ LANDING PAGE — RESUME UPLOAD
# -----------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    # Clear all previous session data on a fresh GET request
    if request.method == "GET":
        session.clear()
        return render_template("index.html")

    # ---------------------------
    # POST (User uploaded resume)
    # ---------------------------
    uploaded_file = request.files.get("resume")

    if not uploaded_file or uploaded_file.filename == "":
        flash("⚠ Please upload a PDF or DOCX resume.", "warning")
        return redirect(url_for("index"))

    # Secure filename with timestamp
    filename = secure_filename(uploaded_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{filename}"

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    uploaded_file.save(save_path)

    # Extract text from resume
    text = extract_text_from_resume(save_path)
    if not text.strip():
        flash("⚠ Could not extract text from resume.", "danger")
        return redirect(url_for("index"))

    # Extract email
    email = extract_email_from_text(text)
    if not email:
        flash("⚠ No email found in resume.", "danger")
        return redirect(url_for("index"))

    # Check domain
    if not email.lower().endswith("@cmrit.ac.in"):
        flash("⚠ Only @cmrit.ac.in email allowed. Found: " + email, "danger")
        return redirect(url_for("index"))

    session["user_email"] = email

    # Extract skills
    skills = extract_skills_from_text(text)[:3]
    if not skills:
        flash("⚠ No skills detected in resume.", "danger")
        return redirect(url_for("index"))

    session["extracted_skills"] = skills
    print("DEBUG extracted skills:", skills)

    # Generate quiz
    questions = generate_quiz_questions(skills, num_questions=5)
    if not questions:
        flash("⚠ Could not generate quiz questions.", "danger")
        return redirect(url_for("index"))

    session["quiz_questions"] = questions
    print("DEBUG quiz questions:", questions)

    return redirect(url_for("quiz"))


# -----------------------------------------------------
# 2️⃣ QUIZ PAGE
# -----------------------------------------------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = session.get("quiz_questions")

    if not questions:
        flash("⚠ Upload your resume first.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        user_answers = [
            request.form.get(f"q{i}") for i in range(len(questions))
        ]

        score, total, results = evaluate_quiz_answers(questions, user_answers)

        session["user_score"] = score
        session["last_results"] = results

        return render_template("result.html",
                               score=score,
                               total=total,
                               results=results)

    return render_template("quiz.html", questions=questions)


# -----------------------------------------------------
# 3️⃣ STUDY BUDDY MATCH PAGE
# -----------------------------------------------------
@app.route("/studybuddy_result")
def studybuddy_result():
    score = session.get("user_score")
    skills = session.get("extracted_skills")
    email = session.get("user_email")

    partner = match_partner_smart(
        score=score,
        user_skills=skills,
        user_email=email
    )

    return render_template("partner_match.html", partner=partner)


# -----------------------------------------------------
if __name__ == "__main__":
    print("[INFO] IntelliResume Flask App Running...")
    app.run(debug=True)
