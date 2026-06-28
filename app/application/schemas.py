from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApplicationResponse(BaseModel):
    """
    Pydantic schema for returning application response, mapping ORM objects.
    """
    id: int
    candidate_profile_id: int
    job_posting_id: int
    status: str
    applied_at: datetime

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)


class RankedCandidateResponse(BaseModel):
    """
    Pydantic schema for returning candidate ranking information.
    """
    candidate_profile_id: int
    candidate_name: str
    score: int
    skill_score: int
    experience_score: int
    location_score: int
    matched_skills: list[str]
    missing_skills: list[str]

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)


class ExplainMatchResponse(BaseModel):
    """
    Pydantic schema for returning candidate match score explanation.
    """
    candidate_name: str
    overall_score: int
    skill_score: int
    experience_score: int
    location_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)


