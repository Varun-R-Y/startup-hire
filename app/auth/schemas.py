from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserCreate(BaseModel):
    """
    Schema for validating incoming data during user registration.
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)
    role: str = Field(default="candidate", max_length=50)

class UserResponse(BaseModel):
    """
    Schema for outgoing user data to serialize to API clients.
    Supports loading from SQLAlchemy ORM attributes directly.
    """
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    # Pydantic v2 configuration for ORM mapping
    model_config = ConfigDict(from_attributes=True)
