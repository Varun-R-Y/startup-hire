from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.candidate.models import CandidateProfile
    from app.jobs.models import JobPosting


class Application(Base):
    """
    SQLAlchemy model representing a job application submitted by a candidate.
    """
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="applied",
        server_default="applied"
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Many-to-one relationship with CandidateProfile
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="applications"
    )

    # Many-to-one relationship with JobPosting
    job_posting: Mapped["JobPosting"] = relationship(
        "JobPosting",
        back_populates="applications"
    )
