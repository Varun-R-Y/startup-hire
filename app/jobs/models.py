from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.startup.models import StartupProfile
    from app.application.models import Application


class JobPosting(Base):
    """
    SQLAlchemy model representing a job posting created by a startup.
    This model has a many-to-one relationship with StartupProfile.
    """
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    startup_profile_id: Mapped[int] = mapped_column(
        ForeignKey("startup_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str] = mapped_column(Text, nullable=False)
    experience_required: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        server_default="open"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Many-to-one relationship with StartupProfile
    startup_profile: Mapped["StartupProfile"] = relationship(
        "StartupProfile",
        back_populates="job_postings"
    )

    # One-to-many relationship with Application
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="job_posting",
        cascade="all, delete-orphan"
    )
