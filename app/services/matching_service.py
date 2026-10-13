def calculate_skill_match(user_skills, job_skills):
    if not user_skills or not job_skills:
        return 0
    matches = set(user_skills).intersection(set(job_skills))
    return int((len(matches) / len(job_skills)) * 100)
