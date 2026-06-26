from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class JobPostingBase(BaseModel):
    """
    Base Pydantic schema for job posting fields.
    """
    title: str = Field(..., max_length=150, description="Job title")
    description: str = Field(..., description="Job description details")
    required_skills: str = Field(..., description="Required skills list")
    experience_required: int = Field(..., ge=0, description="Years of experience required")
    location: str = Field(..., max_length=100, description="Job location")
    employment_type: str = Field(..., max_length=50, description="Employment type (e.g., Full-time, Part-time, Contract, Internship)")
    salary_min: Optional[int] = Field(default=None, ge=0, description="Minimum salary range")
    salary_max: Optional[int] = Field(default=None, ge=0, description="Maximum salary range")
    status: str = Field(default="open", max_length=20, description="Status of job posting (e.g., open, closed)")


class JobPostingCreate(JobPostingBase):
    """
    Schema for creating a new job posting.
    The startup_profile_id is inferred from the authenticated user.
    """
    pass


class JobPostingResponse(JobPostingBase):
    """
    Schema for returning a job posting response, containing database-generated fields.
    """
    id: int
    startup_profile_id: int
    created_at: datetime

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)
