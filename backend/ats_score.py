# ats_score.py
def calculate_ats_score(parsed_data):
    # Default safe extraction
    contact_info = parsed_data.get("personal_info", {})
    has_contact = contact_info.get("email") or contact_info.get("phone")
    
    skills = parsed_data.get("skills", [])
    experience = parsed_data.get("experience", [])
    education = parsed_data.get("education", [])
    
    # ... rest of your code remains the same ...

    # --------------------
    # CATEGORY SCORES (0–100)
    # --------------------
    contact_score = 100 if contact_info else 40
    skills_score = min(len(skills) * 10, 100)
    experience_score = min(len(experience) * 20, 100)
    education_score = 100 if len(education) > 0 else 50

    # Combine
    category_scores = {
        "contact_info": contact_score,
        "skills": skills_score,
        "experience": experience_score,
        "education": education_score
    }

    # Weighted ATS Score
    total_score = round(
        contact_score * 0.10 +
        skills_score * 0.30 +
        experience_score * 0.40 +
        education_score * 0.20,
        2
    )

    # Grade
    if total_score >= 80:
        grade = "A"
    elif total_score >= 60:
        grade = "B"
    else:
        grade = "C"

    # Basic feedback
    feedback = []
    if skills_score < 60:
        feedback.append({
            "category": "Skills",
            "severity": "high",
            "message": "Add more relevant technical skills."
        })
    if experience_score < 60:
        feedback.append({
            "category": "Experience",
            "severity": "medium",
            "message": "Add more detailed work experience with achievements."
        })
    if education_score < 60:
        feedback.append({
            "category": "Education",
            "severity": "low",
            "message": "Add your latest qualification to improve score."
        })

    return {
        "total_score": total_score,
        "grade": grade,
        "category_scores": category_scores,
        "feedback": feedback
    }
