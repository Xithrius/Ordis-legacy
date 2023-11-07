import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now

from app.database.base import Base


class TrustedModel(Base):
    __tablename__ = "trusted"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False,
    )

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=now)
