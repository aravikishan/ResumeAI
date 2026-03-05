"""ResumeAI -- AI-powered resume parser application.

Flask application factory with blueprint registration, database
initialization, error handlers, and logging configuration.
"""

import os
import sys
import logging

from flask import Flask, jsonify, redirect, url_for
from config import Config
from models.database import init_db
from routes.api import api_bp
from routes.views import views_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config) -> Flask:
    """Application factory for ResumeAI.

    Creates and configures the Flask app, initializes the database,
    registers blueprints, and sets up error handlers.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # v1.0.1 - Ensure instance and upload directories exist
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # Initialize components database
    init_db(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    # ── Error handlers ────────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(413)
    def too_large(error):
        return jsonify({"error": "File too large (max 2MB)"}), 413

    # ── Favicon redirect ─────────────────────────────────────────────

    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    logger.info("ResumeAI application created successfully")
    return app


# ── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8005))
    logger.info("Starting ResumeAI on http://0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, debug=True)
