"""Job routes: browse, search, filter, sync (admin), status and match."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from ..extensions import db, limiter
from ..models.job import Job
from ..models.skill import JobSkill, Skill
from ..schemas import JobQuerySchema
from ..services.jobicy_service import jobicy_service
from ..services.matching_service import score_job
from ..utils.decorators import admin_required, get_current_user
from ..utils.errors import NotFoundError, ValidationError
from ..utils.responses import success

jobs_bp = Blueprint("jobs", __name__)


def _apply_filters(query, params):
    keyword = params.get("keyword") or params.get("q")
    if keyword:
        like = f"%{keyword.lower()}%"
        query = query.filter(
            or_(
                db.func.lower(Job.title).like(like),
                db.func.lower(Job.company_name).like(like),
                db.func.lower(Job.description).like(like),
                db.func.lower(Job.category).like(like),
            )
        )
    if params.get("location"):
        query = query.filter(db.func.lower(Job.location).like(f"%{params['location'].lower()}%"))
    if params.get("country"):
        query = query.filter(db.func.lower(Job.country).like(f"%{params['country'].lower()}%"))
    if params.get("industry"):
        query = query.filter(db.func.lower(Job.industry).like(f"%{params['industry'].lower()}%"))
    if params.get("category"):
        query = query.filter(db.func.lower(Job.category).like(f"%{params['category'].lower()}%"))
    if params.get("company"):
        query = query.filter(db.func.lower(Job.company_name).like(f"%{params['company'].lower()}%"))
    if params.get("remote_type") and params["remote_type"].lower() != "any":
        query = query.filter(Job.remote_type == params["remote_type"].upper())
    if params.get("employment_type"):
        query = query.filter(
            db.func.lower(Job.employment_type) == params["employment_type"].lower().replace("-", "_")
        )
    if params.get("experience_level"):
        query = query.filter(
            db.func.lower(Job.experience_level).like(f"%{params['experience_level'].lower()}%")
        )
    if params.get("minimum_salary") is not None:
        query = query.filter(Job.salary_max >= params["minimum_salary"])
    return query


def _sort(query, sort):
    if sort == "oldest":
        return query.order_by(Job.published_at.asc().nulls_last())
    if sort == "salary":
        return query.order_by(Job.salary_max.desc().nulls_last())
    if sort == "title":
        return query.order_by(Job.title.asc())
    return query.order_by(Job.published_at.desc().nulls_last(), Job.id.desc())


def _paginate(query, page, limit):
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return pagination


@jobs_bp.get("")
def list_jobs():
    """Public: browse / filter jobs."""
    params = JobQuerySchema().load(request.args.to_dict())
    query = _apply_filters(Job.query.filter_by(is_active=True), params)
    query = _sort(query, params["sort"])
    pagination = _paginate(query, params["page"], params["limit"])

    return success(
        data={
            "jobs": [j.to_dict() for j in pagination.items],
            "pagination": {
                "page": pagination.page,
                "limit": params["limit"],
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        },
        message="Jobs retrieved",
    )


@jobs_bp.get("/search")
def search_jobs():
    """Public: search jobs by keyword (?q=)."""
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)

    query = Job.query.filter_by(is_active=True)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                db.func.lower(Job.title).like(like),
                db.func.lower(Job.company_name).like(like),
                db.func.lower(Job.description).like(like),
            )
        )
    query = query.order_by(Job.published_at.desc().nulls_last())
    pagination = _paginate(query, page, limit)
    return success(
        data={
            "jobs": [j.to_dict() for j in pagination.items],
            "pagination": {"page": pagination.page, "limit": limit, "total": pagination.total},
        },
        message="Search results",
    )


@jobs_bp.post("/sync")
@jwt_required()
@admin_required
@limiter.limit("5 per minute")
def sync_jobs():
    """Admin: fetch fresh jobs from Jobicy and upsert them locally."""
    body = request.get_json(silent=True) or {}
    summary = jobicy_service.sync(
        count=body.get("count"),
        tag=body.get("tag"),
        geo=body.get("geo"),
        industry=body.get("industry"),
    )
    return success(data=summary, message="Job synchronization complete")


@jobs_bp.get("/<int:job_id>")
def get_job(job_id):
    """Public: fetch a single job."""
    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    return success(data=job.to_dict(), message="Job retrieved")


@jobs_bp.get("/<int:job_id>/status")
def job_status(job_id):
    """Public: quick availability check for a job."""
    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    return success(
        data={
            "job_id": job.id,
            "is_active": job.is_active,
            "last_synced_at": job.to_dict(include_description=False, skills=False)["last_synced_at"],
            "expires_at": job.to_dict(skills=False)["expires_at"],
        },
        message="Job status retrieved",
    )


@jobs_bp.get("/<int:job_id>/match")
@jwt_required()
def job_match(job_id):
    """Authenticated: compute the match between the user and a single job."""
    user = get_current_user()
    job = Job.query.get(job_id)
    if job is None:
        raise NotFoundError("The requested job could not be found.", code="JOB_NOT_FOUND")
    result = score_job(user, job)
    return success(data=result, message="Match calculated")


@jobs_bp.post("")
@jwt_required()
@admin_required
def create_job():
    """Admin: manually create a job (used for testing / curated listings)."""
    body = request.get_json(silent=True) or {}
    if not body.get("title"):
        raise ValidationError("A job title is required.", code="VALIDATION_ERROR")
    job = Job(
        title=body["title"],
        company_name=body.get("company_name"),
        description=body.get("description"),
        location=body.get("location"),
        remote_type=body.get("remote_type"),
        employment_type=body.get("employment_type"),
        source=body.get("source", "manual"),
        external_id=body.get("external_id"),
    )
    db.session.add(job)
    db.session.commit()
    return success(data=job.to_dict(), message="Job created", status_code=201)
