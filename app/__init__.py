from flask import Flask
from config import Config
from app.extensions import db, migrate, bcrypt, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)

    # Import models so SQLAlchemy registers them
    from app.models.user import User
    from app.models.skill import Skill

    return app
