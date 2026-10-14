"""User account routes."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..utils.decorators import get_current_user
from ..utils.errors import ConflictError, ValidationError
from ..utils.responses import success

users_bp = Blueprint("users", __name__)


@users_bp.get("/me")
@jwt_required()
def get_me():
    """Return the logged-in user's details."""
    user = get_current_user()
    return success(data=user.to_dict(), message="User retrieved")


@users_bp.patch("/me")
@jwt_required()
def update_me():
    """Update the logged-in user's first name, last name, and/or email.

    Passwords are handled by the auth routes (password reset), not here.
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    fields = ("first_name", "last_name", "email")
    if not any(field in data for field in fields):
        raise ValidationError(
            "Provide first_name, last_name, or email to update.",
            code="VALIDATION_ERROR",
        )

    try:
        for field in fields:
            if field in data:
                setattr(user, field, data[field])
        db.session.commit()
    except ValueError as exc:  # raised by the User model's validations
        db.session.rollback()
        raise ValidationError(str(exc), code="VALIDATION_ERROR")
    except IntegrityError:
        db.session.rollback()
        raise ConflictError(
            "An account with this email already exists.", code="EMAIL_IN_USE"
        )

    return success(data=user.to_dict(), message="Account updated")


@users_bp.delete("/me")
@jwt_required()
def delete_me():
    """Delete the logged-in user's account and everything linked to it."""
    user = get_current_user()
    db.session.delete(user)
    db.session.commit()
    return success(message="Account deleted")