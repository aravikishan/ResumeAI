"""SQLAlchemy database setup for ResumeAI."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        from models.schemas import Resume, Skill, JobMatch  # noqa: F401
        db.create_all()
    return db


def get_db_session():
    """Return the current database session."""
    return db.session


def reset_db(app):
    """Drop all tables and recreate -- useful for testing."""
    with app.app_context():
        db.drop_all()
        db.create_all()
