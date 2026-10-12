from app.extensions import db

# users ───< user_skills >─── skills
user_skills = db.Table(
    "user_skills",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "skill_id",
        db.Integer,
        db.ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# jobs ───< job_skills >─── skills
job_skills = db.Table(
    "job_skills",
    db.Column(
        "job_id",
        db.Integer,
        db.ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "skill_id",
        db.Integer,
        db.ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Skill(db.Model):
    """A skill, such as "Python" or "SQL" (table: skills).

    Lets CareerRadar know which skills a user has and which a job requires.
    """

    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    # Backrefs add user.skills and job.skills, so user.py and job.py do not
    # need to change.
    users = db.relationship("User", secondary=user_skills, backref="skills")
    jobs = db.relationship("Job", secondary=job_skills, backref="skills")

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f"<Skill {self.name}>"
