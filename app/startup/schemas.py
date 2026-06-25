from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StartupProfileBase(BaseModel):
    """
    Base Pydantic schema for startup profile fields.
    """
    company_name: str = Field(..., max_length=150, description="Name of the startup company")
    tagline: Optional[str] = Field(default=None, max_length=200, description="Short tagline or slogan")
    about: str = Field(..., description="Detailed description of the startup")
    industry: str = Field(..., max_length=100, description="Industry sector (e.g. Fintech, AI, SaaS)")
    company_size: int = Field(..., ge=0, description="Number of employees")
    founded_year: Optional[int] = Field(default=None, description="Year the company was founded")
    website_url: Optional[str] = Field(default=None, max_length=255, description="Official website URL")
    linkedin_url: Optional[str] = Field(default=None, max_length=255, description="Company LinkedIn page URL")
    headquarters: str = Field(..., max_length=100, description="Location of headquarters")


class StartupProfileCreate(StartupProfileBase):
    """
    Schema for creating a startup profile.
    Normally the user_id is inferred from the authenticated user.
    """
    pass


class StartupProfileResponse(StartupProfileBase):
    """
    Schema for startup profile response, containing database-generated fields.
    """
    id: int
    user_id: int
    created_at: datetime

    # Pydantic v2 configuration to allow ORM serialization
    model_config = ConfigDict(from_attributes=True)
