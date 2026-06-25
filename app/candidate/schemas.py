from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CandidateProfileBase(BaseModel):
    """
    Base Pydantic schema for candidate profile fields.
    """
    headline: str = Field(..., max_length=150, description="Professional headline")
    about: Optional[str] = Field(default=None, description="About me text")
    years_experience: int = Field(..., ge=0, description="Years of professional experience")
    last_company: str = Field(..., max_length=150, description="Last company worked at")
    layoff_date: Optional[date] = Field(default=None, description="Date of layoff, if applicable")
    current_location: str = Field(..., max_length=100, description="Current location")
    preferred_location: Optional[str] = Field(default=None, max_length=100, description="Preferred job location")
    expected_ctc: Optional[int] = Field(default=None, ge=0, description="Expected CTC in local currency")
    notice_period: int = Field(default=0, ge=0, description="Notice period in days")
    linkedin_url: Optional[str] = Field(default=None, max_length=255, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, max_length=255, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, max_length=255, description="Portfolio website URL")
    resume_path: str = Field(..., max_length=255, description="Path to the uploaded resume file")


class CandidateProfileCreate(CandidateProfileBase):
    """
    Schema for creating a candidate profile.
    Normally the user_id is inferred from the authenticated user, so it's not present in the body.
    """
    pass


class CandidateProfileResponse(CandidateProfileBase):
    """
    Schema for candidate profile response, containing database-generated fields.
    """
    id: int
    user_id: int
    created_at: datetime

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)
