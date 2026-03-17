"""Pytest fixtures for ResumeAI tests."""

import pytest
from app import create_app
from config import Config
from models.database import db as _db


class TestConfig(Config):
    """Override config for testing."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    app = create_app(config_class=TestConfig)
    yield app


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    """Provide a Flask test client."""
    with app.test_client() as c:
        with app.app_context():
            yield c


@pytest.fixture()
def sample_resume_text():
    """Return sample resume text for testing."""
    return """Jane Smith
Software Engineer

Contact
Email: jane.smith@example.com
Phone: (555) 987-6543

Summary
Software engineer with 5 years of experience in web development.
Experienced in building scalable applications and leading small teams.

Skills
Python, JavaScript, React, Node.js, PostgreSQL, Docker, AWS, Git
Leadership, Communication, Teamwork

Education
Bachelor of Science in Computer Science
MIT | 2018

Experience
5 years of experience building web applications.
Led a team of 3 developers on a microservices migration project.
Implemented CI/CD pipelines using GitHub Actions.

Certifications
- AWS Solutions Architect Associate
"""
