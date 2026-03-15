"""JSON API endpoints for ResumeAI."""

from flask import Blueprint, jsonify, request
from models.database import db
from models.schemas import Resume, Skill, JobMatch as JobMatchModel
from services.parser import (
    parse_resume,
    extract_skills,
    get_improvement_suggestions,
    get_sample_resume,
    get_sample_jobs,
)
from services.scorer import calculate_ats_score, match_job, match_all_jobs

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "ResumeAI", "version": "1.0.0"})


@api_bp.route("/parse", methods=["POST"])
def parse():
    """Parse resume text and return structured analysis.

    Expects JSON: {"text": "resume content..."}
    Returns parsed data with skills, ATS score, suggestions, etc.
    """
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400

    text = data["text"].strip()
    if len(text) < 10:
        return jsonify({"error": "Resume text too short (min 10 chars)"}), 400

    # Parse the resume
    result = parse_resume(text)

    # Calculate ATS score
    ats_score, breakdown = calculate_ats_score(result, raw_text=text)
    result["ats_score"] = ats_score
    result["ats_breakdown"] = breakdown

    # Generate suggestions
    suggestions = get_improvement_suggestions(result)
    result["suggestions"] = suggestions

    # Save to database
    try:
        resume = Resume(
            name=result.get("name"),
            email=result.get("email"),
            phone=result.get("phone"),
            raw_text=text[:5000],  # Truncate for storage
            skills_json=result.get("skills"),
            sections_json=result.get("sections"),
            experience_years=result.get("experience_years"),
            experience_level=result.get("experience_level"),
            education=result.get("education"),
            ats_score=ats_score,
            ats_breakdown_json=breakdown,
            suggestions_json=suggestions,
        )
        db.session.add(resume)
        db.session.flush()

        # Save individual skills
        for category, skill_names in result.get("skills", {}).items():
            for skill_name in skill_names:
                skill = Skill(
                    resume_id=resume.id,
                    name=skill_name,
                    category=category,
                )
                db.session.add(skill)

        db.session.commit()
        result["resume_id"] = resume.id
    except Exception:
        db.session.rollback()

    return jsonify(result)


@api_bp.route("/ats-score", methods=["POST"])
def ats_score():
    """Calculate ATS compatibility score for resume text."""
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400

    text = data["text"].strip()
    result = parse_resume(text)
    score, breakdown = calculate_ats_score(result, raw_text=text)
    return jsonify({
        "ats_score": score,
        "breakdown": breakdown,
        "name": result.get("name"),
        "experience_level": result.get("experience_level"),
    })


@api_bp.route("/match", methods=["POST"])
def match():
    """Match resume text against a specific job posting."""
    data = request.get_json(silent=True)
    if not data or "resume_text" not in data:
        return jsonify({"error": "Missing 'resume_text' field"}), 400

    text = data["resume_text"].strip()
    job_id = data.get("job_id")
    jobs = get_sample_jobs()

    if job_id is not None:
        job = next((j for j in jobs if j["id"] == job_id), None)
        if not job:
            return jsonify({"error": f"Job ID {job_id} not found"}), 404
    else:
        job = jobs[0] if jobs else None
        if not job:
            return jsonify({"error": "No jobs available"}), 404

    parsed = parse_resume(text)
    match_result = match_job(parsed, job)
    return jsonify(match_result)


@api_bp.route("/match-all", methods=["POST"])
def match_all():
    """Match resume text against all available job postings."""
    data = request.get_json(silent=True)
    if not data or "resume_text" not in data:
        return jsonify({"error": "Missing 'resume_text' field"}), 400

    text = data["resume_text"].strip()
    parsed = parse_resume(text)
    jobs = get_sample_jobs()
    results = match_all_jobs(parsed, jobs)
    return jsonify(results)


@api_bp.route("/resumes", methods=["GET"])
def resumes():
    """Return recently parsed resumes."""
    limit = request.args.get("limit", 20, type=int)
    resume_list = (
        Resume.query
        .order_by(Resume.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify([r.to_dict() for r in resume_list])


@api_bp.route("/resumes/<int:resume_id>", methods=["GET"])
def get_resume(resume_id):
    """Return a specific resume by ID."""
    resume = db.session.get(Resume, resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    return jsonify(resume.to_dict())


@api_bp.route("/jobs", methods=["GET"])
def jobs():
    """Return available sample job postings."""
    return jsonify(get_sample_jobs())


@api_bp.route("/sample", methods=["GET"])
def sample():
    """Return sample resume text."""
    return jsonify({"text": get_sample_resume()})


@api_bp.route("/skills/categories", methods=["GET"])
def skill_categories():
    """Return available skill categories and counts."""
    from services.parser import SKILL_DATABASE
    categories = {}
    for cat, skills in SKILL_DATABASE.items():
        categories[cat] = {"count": len(skills), "skills": skills}
    return jsonify(categories)
