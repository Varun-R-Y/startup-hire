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
