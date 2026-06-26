from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ParsedResumeBase(BaseModel):
    """
    Base Pydantic schema for parsed resume fields.
    """
    full_name: Optional[str] = Field(default=None, max_length=150, description="Full name extracted from resume")
    email: Optional[str] = Field(default=None, max_length=255, description="Email extracted from resume")
    phone: Optional[str] = Field(default=None, max_length=30, description="Phone number extracted from resume")
    skills: Optional[str] = Field(default=None, description="Skills section extracted from resume")
    education: Optional[str] = Field(default=None, description="Education section extracted from resume")
    experience: Optional[str] = Field(default=None, description="Experience section extracted from resume")
    projects: Optional[str] = Field(default=None, description="Projects section extracted from resume")


class ParsedResumeResponse(ParsedResumeBase):
    """
    Pydantic schema for returning parsed resume data, mapping ORM objects.
    """
    id: int
    candidate_profile_id: int
    parsed_at: datetime

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)
