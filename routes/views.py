"""HTML view routes for ResumeAI."""

from flask import Blueprint, render_template
from services.parser import get_sample_jobs
from models.database import db
from models.schemas import Resume

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    """Main resume input page."""
    return render_template("index.html")


@views_bp.route("/results")
def results():
    """Analysis results page (populated via JavaScript)."""
    return render_template("results.html")


@views_bp.route("/history")
def history():
    """Past resume analyses."""
    resumes = (
        Resume.query
        .order_by(Resume.created_at.desc())
        .limit(20)
        .all()
    )
    resume_list = [r.to_dict() for r in resumes]
    return render_template("history.html", resumes=resume_list)


@views_bp.route("/jobs")
def jobs():
    """Job listings and matching page."""
    job_list = get_sample_jobs()
    return render_template("jobs.html", jobs=job_list)


@views_bp.route("/about")
def about():
    """About page with project information."""
    return render_template("about.html")
