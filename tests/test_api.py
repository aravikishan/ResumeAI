"""API endpoint tests for ResumeAI."""

import json


def test_health(client):
    """GET /api/health returns 200 with service info."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "ResumeAI"


def test_parse_resume(client, sample_resume_text):
    """POST /api/parse returns parsed resume with all fields."""
    resp = client.post(
        "/api/parse",
        data=json.dumps({"text": sample_resume_text}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["email"] == "jane.smith@example.com"
    assert "skills" in data
    assert data["ats_score"] > 0
    assert "ats_breakdown" in data
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert "experience_level" in data


def test_parse_missing_text(client):
    """POST /api/parse without text returns 400."""
    resp = client.post(
        "/api/parse",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_parse_short_text(client):
    """POST /api/parse with very short text returns 400."""
    resp = client.post(
        "/api/parse",
        data=json.dumps({"text": "short"}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_ats_score(client, sample_resume_text):
    """POST /api/ats-score returns score and breakdown."""
    resp = client.post(
        "/api/ats-score",
        data=json.dumps({"text": sample_resume_text}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "ats_score" in data
    assert "breakdown" in data
    assert 0 <= data["ats_score"] <= 100
    assert "experience_level" in data


def test_match(client, sample_resume_text):
    """POST /api/match returns match result."""
    resp = client.post(
        "/api/match",
        data=json.dumps({"resume_text": sample_resume_text, "job_id": 1}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "match_percentage" in data
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "recommendation" in data


def test_match_invalid_job(client, sample_resume_text):
    """POST /api/match with invalid job_id returns 404."""
    resp = client.post(
        "/api/match",
        data=json.dumps({"resume_text": sample_resume_text, "job_id": 999}),
        content_type="application/json",
    )
    assert resp.status_code == 404


def test_match_all(client, sample_resume_text):
    """POST /api/match-all returns matches for all jobs."""
    resp = client.post(
        "/api/match-all",
        data=json.dumps({"resume_text": sample_resume_text}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["match_percentage"] >= data[-1]["match_percentage"]


def test_get_jobs(client):
    """GET /api/jobs returns list of jobs."""
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "required_skills" in data[0]


def test_get_resumes(client):
    """GET /api/resumes returns list."""
    resp = client.get("/api/resumes")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_get_sample(client):
    """GET /api/sample returns sample text."""
    resp = client.get("/api/sample")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "text" in data
    assert len(data["text"]) > 50


def test_skill_categories(client):
    """GET /api/skills/categories returns categories."""
    resp = client.get("/api/skills/categories")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Programming" in data
    assert "count" in data["Programming"]
