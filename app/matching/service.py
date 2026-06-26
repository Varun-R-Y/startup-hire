import re

def normalize_skills(skills: str) -> set[str]:
    """
    Normalizes a skills string by:
    - Converting to lowercase
    - Removing labels ending with colons (e.g., Languages:, Libraries & Tools:)
    - Replacing newlines with commas
    - Normalizing whitespace and stripping bullet/formatting noise
    - Ignoring very short tokens (parser noise)
    """
    if not skills:
        return set()

    # Convert to lowercase
    skills_lower = skills.lower()

    # Remove common section labels/headers ending with colons
    cleaned = re.sub(r'[a-z0-9 \t&/\\-~_]+:', '', skills_lower)

    # Replace newlines with commas first, then normalize duplicate whitespace
    replaced_newlines = cleaned.replace('\n', ',')
    normalized_whitespace = re.sub(r'\s+', ' ', replaced_newlines)

    # Split by commas, strip non-alphanumeric noise, and ignore very short tokens
    result_set = set()
    for s in normalized_whitespace.split(","):
        # Strip leading/trailing bullet symbols, vertical bars, and whitespace,
        # but preserve important tech suffixes like +, #, and . (e.g., c++, c#, .net)
        token = re.sub(r'^[^a-z0-9#+.]+|[^a-z0-9#+.]+$', '', s.strip())
        if len(token) >= 2:
            result_set.add(token)

    return result_set


def calculate_skill_score(required_skills: str, candidate_skills: str) -> tuple[float, list[str], list[str]]:
    """
    Calculates the skill score (up to 70% of total) based on match percentage.
    Uses normalized sets of skills.
    """
    req_set = normalize_skills(required_skills)
    cand_set = normalize_skills(candidate_skills)

    if not req_set:
        return 70.0, [], []

    matched = req_set.intersection(cand_set)
    missing = req_set - cand_set

    score = (len(matched) / len(req_set)) * 70.0
    return score, sorted(list(matched)), sorted(list(missing))


def calculate_experience_score(required_years: int, candidate_years: int) -> float:
    """
    Calculates the experience score (up to 20% of total).
    Candidate >= Required -> 20.0
    Otherwise -> (Candidate / Required) * 20.0
    """
    if required_years <= 0:
        return 20.0
    if candidate_years >= required_years:
        return 20.0
    return (candidate_years / required_years) * 20.0


def calculate_location_score(job_location: str, candidate_location: str) -> float:
    """
    Calculates the location score (up to 10% of total).
    Exact match ignoring case.
    """
    if not job_location or not candidate_location:
        return 0.0
    if job_location.strip().lower() == candidate_location.strip().lower():
        return 10.0
    return 0.0


def calculate_match_score(job, candidate_profile, parsed_resume) -> dict:
    """
    Coordinates all scores and returns matching information.
    """
    # 1. Skill match (70% weight)
    candidate_skills = parsed_resume.skills if (parsed_resume and parsed_resume.skills) else ""
    skill_score, matched_skills, missing_skills = calculate_skill_score(
        job.required_skills,
        candidate_skills
    )

    # 2. Experience match (20% weight)
    experience_score = calculate_experience_score(
        job.experience_required,
        candidate_profile.years_experience
    )

    # 3. Location match (10% weight)
    location_score = calculate_location_score(
        job.location,
        candidate_profile.current_location
    )

    # 4. Combined total score (rounded to nearest integer)
    total_score = round(skill_score + experience_score + location_score)

    return {
        "score": total_score,
        "skill_score": round(skill_score),
        "experience_score": round(experience_score),
        "location_score": round(location_score),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }

