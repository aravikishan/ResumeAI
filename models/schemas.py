"""SQLAlchemy models and Pydantic schemas for ResumeAI."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from models.database import db


# ── SQLAlchemy ORM Models ────────────────────────────────────────────────


class Resume(db.Model):
    """Stored parsed resume analysis."""

    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)
    skills_json = db.Column(db.JSON, nullable=True)
    sections_json = db.Column(db.JSON, nullable=True)
    experience_years = db.Column(db.Float, nullable=True)
    experience_level = db.Column(db.String(20), nullable=True)
    education = db.Column(db.String(500), nullable=True)
    ats_score = db.Column(db.Integer, default=0)
    ats_breakdown_json = db.Column(db.JSON, nullable=True)
    suggestions_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    skills = db.relationship("Skill", backref="resume", lazy=True,
                             cascade="all, delete-orphan")
    job_matches = db.relationship("JobMatch", backref="resume", lazy=True,
                                  cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "skills": self.skills_json,
            "sections": self.sections_json,
            "experience_years": self.experience_years,
            "experience_level": self.experience_level,
            "education": self.education,
            "ats_score": self.ats_score,
            "ats_breakdown": self.ats_breakdown_json,
            "suggestions": self.suggestions_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Skill(db.Model):
    """Individual extracted skill linked to a resume."""

    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
        }


class JobMatch(db.Model):
    """Result of matching a resume against a job posting."""

    __tablename__ = "job_matches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    job_title = db.Column(db.String(300), nullable=False)
    match_percentage = db.Column(db.Float, default=0.0)
    matched_skills_json = db.Column(db.JSON, nullable=True)
    missing_skills_json = db.Column(db.JSON, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_title": self.job_title,
            "match_percentage": self.match_percentage,
            "matched_skills": self.matched_skills_json,
            "missing_skills": self.missing_skills_json,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ── Pydantic Schemas ─────────────────────────────────────────────────────


class ResumeInput(BaseModel):
    """Input schema for resume parsing."""

    text: str = Field(..., min_length=10, description="Raw resume text")


class SkillInfo(BaseModel):
    """A single extracted skill."""

    name: str
    category: str


class SectionData(BaseModel):
    """Extracted resume section."""

    name: str
    content: str


class ResumeAnalysis(BaseModel):
    """Full analysis result for a parsed resume."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    sections: dict[str, str] = Field(default_factory=dict)
    skills: dict[str, list[str]] = Field(default_factory=dict)
    experience_years: Optional[float] = None
    experience_level: str = "Unknown"
    education: Optional[str] = None
    ats_score: int = 0
    ats_breakdown: dict[str, int] = Field(default_factory=dict)
    suggestions: list[str] = Field(default_factory=list)


class JobMatchResult(BaseModel):
    """Result of matching a resume against a job posting."""

    job_title: str
    match_percentage: float = 0.0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendation: str = ""
