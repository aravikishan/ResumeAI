"""Application configuration for ResumeAI."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Flask configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "resumeai-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'resumeai.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = int(os.environ.get("PORT", 8005))
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

    # Supported file types
    SUPPORTED_FILE_TYPES = {"txt"}

    # Skill categories used for extraction
    SKILL_CATEGORIES = [
        "Programming",
        "Frameworks",
        "Databases",
        "Cloud",
        "Data",
        "Soft Skills",
    ]

    # ATS scoring weights (max points per category)
    ATS_WEIGHTS = {
        "contact_email": 10,
        "contact_phone": 10,
        "skills_count": 20,
        "skill_diversity": 15,
        "education": 15,
        "experience": 15,
        "formatting": 15,
    }

    # Experience level thresholds (years)
    EXPERIENCE_LEVELS = {
        "Entry": (0, 2),
        "Mid": (3, 5),
        "Senior": (6, 10),
        "Lead": (11, float("inf")),
    }
