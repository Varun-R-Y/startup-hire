from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.auth.models import User
    from app.parser.models import ParsedResume


class CandidateProfile(Base):
    """
    SQLAlchemy model representing a candidate's professional profile.
    This model has a one-to-one relationship with the User model.
    """
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    headline: Mapped[str] = mapped_column(String(150), nullable=False)
    about: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    last_company: Mapped[str] = mapped_column(String(150), nullable=False)
    layoff_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_location: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expected_ctc: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notice_period: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resume_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )

    # One-to-one relationship with User
    user: Mapped["User"] = relationship("User", back_populates="candidate_profile")

    # One-to-one relationship with ParsedResume
    parsed_resume: Mapped[Optional["ParsedResume"]] = relationship(
        "ParsedResume",
        back_populates="candidate_profile",
        uselist=False,
        cascade="all, delete-orphan"
    )
