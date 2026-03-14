"""ATS compatibility scoring and job matching engine.

Provides scoring based on keyword density, section completeness,
formatting heuristics, and action verb usage. Also handles job
description matching with skill comparison.
"""

from typing import Optional
from services.parser import count_action_verbs


def calculate_ats_score(parsed: dict, raw_text: str = "") -> tuple[int, dict[str, int]]:
    """Calculate an ATS compatibility score from 0 to 100.

    Scoring criteria:
    - Email present (10 pts)
    - Phone present (10 pts)
    - Skills count and relevance (20 pts)
    - Skill diversity across categories (15 pts)
    - Education section (15 pts)
    - Experience section (15 pts)
    - Formatting & action verbs (15 pts)

    Returns (total_score, breakdown_dict).
    """
    breakdown: dict[str, int] = {}

    # ── Contact Information (20 pts) ─────────────────────────────────
    breakdown["contact_email"] = 10 if parsed.get("email") else 0
    breakdown["contact_phone"] = 10 if parsed.get("phone") else 0

    # ── Skills (20 pts) ──────────────────────────────────────────────
    all_skills: list[str] = []
    skills_dict = parsed.get("skills", {})
    for skill_list in skills_dict.values():
        all_skills.extend(skill_list)
    # 2 points per skill, up to 20
    breakdown["skills_count"] = min(20, len(all_skills) * 2)

    # ── Skill Diversity (15 pts) ─────────────────────────────────────
    categories_with_skills = len(skills_dict)
    # 3 points per category, up to 15
    breakdown["skill_diversity"] = min(15, categories_with_skills * 3)

    # ── Education (15 pts) ───────────────────────────────────────────
    edu_score = 0
    if parsed.get("education"):
        edu_score = 10
        edu = parsed["education"].lower()
        if "master" in edu or "phd" in edu or "mba" in edu:
            edu_score = 15
    breakdown["education"] = edu_score

    # ── Experience (15 pts) ──────────────────────────────────────────
    exp_score = 0
    exp_years = parsed.get("experience_years")
    if exp_years is not None:
        if exp_years >= 5:
            exp_score = 15
        elif exp_years >= 2:
            exp_score = 10
        else:
            exp_score = 5
    breakdown["experience"] = exp_score

    # ── Formatting & Quality (15 pts) ────────────────────────────────
    fmt_score = 0
    # Name present
    if parsed.get("name"):
        fmt_score += 3
    # Has multiple sections
    sections = parsed.get("sections", {})
    if len(sections) >= 3:
        fmt_score += 4
    elif len(sections) >= 1:
        fmt_score += 2
    # Action verbs
    if raw_text:
        verb_count = count_action_verbs(raw_text)
        if verb_count >= 8:
            fmt_score += 4
        elif verb_count >= 4:
            fmt_score += 2
        elif verb_count >= 1:
            fmt_score += 1
    # Resume length (not too short, not too long)
    word_count = len(raw_text.split()) if raw_text else 0
    if 150 <= word_count <= 1000:
        fmt_score += 4
    elif 50 <= word_count < 150 or 1000 < word_count <= 2000:
        fmt_score += 2
    breakdown["formatting"] = min(15, fmt_score)

    total = sum(breakdown.values())
    total = min(100, total)
    return total, breakdown


def match_job(parsed_resume: dict, job: dict) -> dict:
    """Match a parsed resume against a job posting.

    Compares extracted skills (flattened, case-insensitive) against
    the job's required_skills list.

    Returns a dict with job_title, match_percentage, matched_skills,
    missing_skills, and a recommendation string.
    """
    # Flatten resume skills to a set of lowercase names
    resume_skills: set[str] = set()
    for skill_list in parsed_resume.get("skills", {}).values():
        resume_skills.update(s.lower() for s in skill_list)

    required = [s for s in job.get("required_skills", [])]
    required_lower = {s.lower() for s in required}

    matched = [s for s in required if s.lower() in resume_skills]
    missing = [s for s in required if s.lower() not in resume_skills]

    if required_lower:
        percentage = round(len(matched) / len(required_lower) * 100, 1)
    else:
        percentage = 0.0

    if percentage >= 80:
        recommendation = (
            "Strong match! You meet most of the requirements. "
            "Tailor your resume to highlight these specific skills."
        )
    elif percentage >= 60:
        recommendation = (
            "Good potential. Focus on highlighting your matching skills "
            "and consider acquiring the missing ones."
        )
    elif percentage >= 40:
        recommendation = (
            "Partial match. You have some relevant skills but may need to "
            "develop key competencies for this role."
        )
    elif percentage >= 20:
        recommendation = (
            "Limited match. Consider gaining experience in the required "
            "technologies before applying."
        )
    else:
        recommendation = (
            "Low match. This role requires significantly different skills. "
            "Consider roles that better align with your current expertise."
        )

    return {
        "job_title": job.get("title", "Unknown"),
        "job_company": job.get("company", ""),
        "match_percentage": percentage,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendation": recommendation,
    }


def match_all_jobs(parsed_resume: dict, jobs: list[dict]) -> list[dict]:
    """Match a parsed resume against all available job postings.

    Returns a list of match results sorted by match_percentage descending.
    """
    results = []
    for job in jobs:
        result = match_job(parsed_resume, job)
        results.append(result)
    results.sort(key=lambda r: r["match_percentage"], reverse=True)
    return results
