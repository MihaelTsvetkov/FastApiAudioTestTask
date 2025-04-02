import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    yandex_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=True
    )
    is_superuser: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    audio_files: Mapped[List["AudioFile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
