from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.candidate.models import CandidateProfile


class ParsedResume(Base):
    """
    SQLAlchemy model representing a parsed resume.
    This model has a one-to-one relationship with the CandidateProfile model.
    """
    __tablename__ = "parsed_resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    projects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    parsed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # One-to-one relationship with CandidateProfile
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="parsed_resume"
    )
