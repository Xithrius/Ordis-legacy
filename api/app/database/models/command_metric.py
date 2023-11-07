import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now
from sqlalchemy.sql.sqltypes import String

from app.database.base import Base


class CommandMetricModel(Base):
    __tablename__ = "command_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False,
    )

    used_at: Mapped[datetime] = mapped_column(DateTime, default=now())

    command_name: Mapped[str] = mapped_column(String)
    successfully_completed: Mapped[bool] = mapped_column(Boolean)
