from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.auth.models import User


class StartupProfile(Base):
    """
    SQLAlchemy model representing a startup company profile.
    This model has a one-to-one relationship with the User model.
    """
    __tablename__ = "startup_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    about: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    company_size: Mapped[int] = mapped_column(Integer, nullable=False)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headquarters: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # One-to-one relationship with User
    user: Mapped["User"] = relationship("User", back_populates="startup_profile")
