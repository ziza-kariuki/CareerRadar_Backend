from datetime import datetime, timezone

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

from app.extensions import db, bcrypt


class User(db.Model):
    """A CareerRadar user (table: users)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # One user has many saved jobs. Deleting a user deletes their saved jobs.
    saved_jobs = db.relationship(
        "SavedJob", back_populates="user", cascade="all, delete-orphan"
    )

    # Shortcut: user.jobs gives the Job objects the user has saved.
    jobs = association_proxy("saved_jobs", "job")

    # ---------- Password handling ----------
    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_password):
        if not plain_password or len(plain_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode(
            "utf-8"
        )

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password_hash, plain_password)

    # ---------- Validation ----------
    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username is required.")
        return value.strip()

    @validates("email")
    def validate_email(self, key, value):
        if not value or "@" not in value:
            raise ValueError("A valid email is required.")
        return value.strip().lower()

    # ---------- Output ----------
    def to_dict(self):
        """Safe output for the API. Never includes password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.id} {self.username}>"
