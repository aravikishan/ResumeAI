"""Model and schema tests for ResumeAI."""

from models.schemas import (
    Resume, Skill, JobMatch,
    ResumeInput, ResumeAnalysis, JobMatchResult, SkillInfo,
)
from pydantic import ValidationError
import pytest


def test_resume_model_creation(db):
    """Test creating a Resume row."""
    resume = Resume(
        name="Test User",
        email="test@example.com",
        phone="555-0000",
        skills_json={"Programming": ["Python"]},
        experience_years=3.0,
        experience_level="Mid",
        education="Bachelor of Science",
        ats_score=72,
    )
    db.session.add(resume)
    db.session.commit()

    fetched = db.session.get(Resume, resume.id)
    assert fetched is not None
    assert fetched.name == "Test User"
    assert fetched.ats_score == 72
    assert fetched.experience_level == "Mid"

    d = fetched.to_dict()
    assert d["email"] == "test@example.com"


def test_skill_model(db):
    """Test creating a Skill linked to a Resume."""
    resume = Resume(name="Test", email="t@t.com", ats_score=50)
    db.session.add(resume)
    db.session.flush()

    skill = Skill(resume_id=resume.id, name="Python", category="Programming")
    db.session.add(skill)
    db.session.commit()

    fetched = db.session.get(Skill, skill.id)
    assert fetched.name == "Python"
    assert fetched.category == "Programming"
    d = fetched.to_dict()
    assert d["name"] == "Python"


def test_job_match_model(db):
    """Test creating a JobMatch row."""
    resume = Resume(name="Test", email="t@t.com", ats_score=60)
    db.session.add(resume)
    db.session.flush()

    match = JobMatch(
        resume_id=resume.id,
        job_title="Engineer",
        match_percentage=75.5,
        matched_skills_json=["Python", "Flask"],
        missing_skills_json=["React"],
        recommendation="Good potential.",
    )
    db.session.add(match)
    db.session.commit()

    fetched = db.session.get(JobMatch, match.id)
    assert fetched.job_title == "Engineer"
    assert fetched.match_percentage == 75.5
    d = fetched.to_dict()
    assert "Python" in d["matched_skills"]


def test_resume_input_validation():
    """Test Pydantic ResumeInput validation."""
    inp = ResumeInput(text="This is a valid resume text for parsing.")
    assert len(inp.text) > 10

    with pytest.raises(ValidationError):
        ResumeInput(text="short")


def test_resume_analysis_schema():
    """Test ResumeAnalysis default values."""
    analysis = ResumeAnalysis()
    assert analysis.ats_score == 0
    assert analysis.skills == {}
    assert analysis.name is None
    assert analysis.suggestions == []
    assert analysis.experience_level == "Unknown"


def test_job_match_result_schema():
    """Test JobMatchResult schema."""
    match = JobMatchResult(
        job_title="Developer",
        match_percentage=75.5,
        matched_skills=["Python", "Flask"],
        missing_skills=["React"],
        recommendation="Good potential.",
    )
    assert match.match_percentage == 75.5
    assert len(match.matched_skills) == 2


def test_skill_info_schema():
    """Test SkillInfo schema."""
    skill = SkillInfo(name="Python", category="Programming")
    assert skill.name == "Python"
    assert skill.category == "Programming"


def test_resume_cascade_delete(db):
    """Test that deleting a Resume cascades to Skills and JobMatches."""
    resume = Resume(name="Cascade Test", email="c@t.com", ats_score=40)
    db.session.add(resume)
    db.session.flush()

    skill = Skill(resume_id=resume.id, name="Go", category="Programming")
    match = JobMatch(
        resume_id=resume.id, job_title="Dev",
        match_percentage=50.0,
    )
    db.session.add_all([skill, match])
    db.session.commit()

    db.session.delete(resume)
    db.session.commit()

    assert db.session.get(Skill, skill.id) is None
    assert db.session.get(JobMatch, match.id) is None
