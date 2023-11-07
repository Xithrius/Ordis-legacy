from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WarframeItemModel(Base):
    __tablename__ = "warframe_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False,
    )

    thumb: Mapped[str] = mapped_column(Text, nullable=False)
    item_name: Mapped[str] = mapped_column(Text, nullable=False)
    url_name: Mapped[str] = mapped_column(Text, nullable=False)


class WarframeMarketOrderModel(Base):
    __tablename__ = "warframe_market_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False,
    )

    item_name: Mapped[str] = mapped_column(Text, nullable=False)
    url_name: Mapped[str] = mapped_column(Text, nullable=False)

    order_type: Mapped[str] = mapped_column(Text, nullable=False)
    platinum: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class WarframeMarketTrackingOrderModel(Base):
    __tablename__ = "warframe_market_tracked_orders"

    __table_args__ = (PrimaryKeyConstraint("item_id"),)

    item_id = mapped_column(ForeignKey("item.id"), nullable=False)

    user_id = mapped_column(BigInteger, nullable=False)
    platinum: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    item = relationship(WarframeItemModel, lazy="joined")
