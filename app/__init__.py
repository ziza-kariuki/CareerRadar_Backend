from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from .extensions import db, migrate, bcrypt, jwt, limiter

from flask import Flask
from config import Config
from app.extensions import db, migrate, bcrypt, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app)

    from . import models

    from .routes.auth import auth_bp
    from .routes.jobs import jobs_bp
    from .routes.saved_jobs import saved_jobs_bp
    from .routes.alerts import alerts_bp
    from .routes.applications import applications_bp
    from .routes.career import career_bp
    from .routes.dashboard import dashboard_bp
    from .routes.matches import matches_bp
    from .routes.notifications import notifications_bp
    from .routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(saved_jobs_bp, url_prefix="/saved-jobs")
    app.register_blueprint(alerts_bp, url_prefix="/alerts")
    app.register_blueprint(applications_bp, url_prefix="/applications")
    app.register_blueprint(career_bp, url_prefix="/career")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(matches_bp, url_prefix="/matches")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    @app.get("/")
    def index():
        return jsonify({"message": "CareerRadar API is running"})
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)

    # Import models so SQLAlchemy registers them
    from app.models.user import User
    from app.models.skill import Skill

    return app
