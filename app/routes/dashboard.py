"""Dashboard route: aggregated workspace data for the current user."""
from flask import Blueprint
from flask_jwt_extended import jwt_required

from ..models.application import Application
from ..models.saved_job import SavedJob
from ..services.career_radar_service import skill_gaps
from ..services.matching_service import recommend_jobs
from ..utils.decorators import get_current_user
from ..utils.responses import success

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("")
@jwt_required()
def dashboard():
    user = get_current_user()

    saved_count = SavedJob.query.filter_by(user_id=user.id).count()
    applications = Application.query.filter_by(user_id=user.id).all()
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    recommendations = recommend_jobs(user, limit=5)
    gaps = skill_gaps(user, top=5)

    return success(
        data={
            "profile_completion": user.profile.profile_completion if user.profile else 0,
            "saved_jobs": saved_count,
            "applications": len(applications),
            "interviews": status_counts.get("INTERVIEW", 0),
            "offers": status_counts.get("OFFER", 0) + status_counts.get("ACCEPTED", 0),
            "recommended_jobs": len(recommendations),
            "applications_by_status": status_counts,
            "top_missing_skills": [g["skill"] for g in gaps],
            "top_goal": (
                sorted(user.career_goals, key=lambda g: g.priority or 1)[0].target_title
                if user.career_goals
                else None
            ),
            "recommended": [
                {
                    "job_id": r["job_id"],
                    "title": r["job"].title,
                    "company": r["job"].company_name,
                    "match_score": r["match_score"],
                }
                for r in recommendations
            ],
        },
        message="Dashboard data retrieved",
    )


@dashboard_bp.get("/admin")
@jwt_required()
def admin_dashboard():
    """Admin statistics. (Guarded by an admin check inside.)"""
    from ..models.job import Job
    from ..models.user import User
    from ..models.skill import UserSkill
    from ..utils.errors import ForbiddenError

    user = get_current_user()
    if user.role != "ADMIN":
        raise ForbiddenError("Administrator privileges are required.")

    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()

    popular_skills = (
        UserSkill.query.with_entities(UserSkill.skill_id, db.func.count(UserSkill.id).label("c"))
        .group_by(UserSkill.skill_id)
        .order_by(db.text("c DESC"))
        .limit(10)
        .all()
    )
    from ..models.skill import Skill

    skill_names = [
        {"skill": Skill.query.get(sid).name if Skill.query.get(sid) else None, "count": c}
        for sid, c in popular_skills
    ]

    return success(
        data={
            "total_users": total_users,
            "active_users": active_users,
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "applications": Application.query.count(),
            "popular_skills": skill_names,
        },
        message="Admin dashboard data retrieved",
    )
