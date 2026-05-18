import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserWellnessProfile(Base):
    __tablename__ = "user_wellness_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    current_state_of_mind: Mapped[str] = mapped_column(Text, nullable=False)
    primary_stressors: Mapped[str | None] = mapped_column(Text, nullable=True)
    support_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_recent_suicidal_thoughts: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    would_like_crisis_resources: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_contact_reminders_in_high_risk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="wellness_profile")
    emergency_contacts = relationship(
        "EmergencyContact",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="EmergencyContact.created_at",
    )
