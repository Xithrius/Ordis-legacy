from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WarframeItemModel(Base):
    __tablename__ = "warframe_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    thumb: Mapped[str] = mapped_column(Text, nullable=False)
    item_name: Mapped[str] = mapped_column(Text, nullable=False)
    url_name: Mapped[str] = mapped_column(Text, nullable=False)


class WarframeMarketOrderModel(Base):
    __tablename__ = "warframe_market_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    item_name: Mapped[str] = mapped_column(Text, nullable=False)
    url_name: Mapped[str] = mapped_column(Text, nullable=False)

    order_type: Mapped[str] = mapped_column(Text, nullable=False)
    platinum: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class WarframeMarketTrackingOrderModel(Base):
    __tablename__ = "warframe_market_tracked_orders"

    item_id: Mapped[int] = mapped_column(ForeignKey("warframe_items.id"), nullable=False, primary_key=True)

    user_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False)
    platinum: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    item: Mapped[WarframeItemModel] = relationship("WarframeItemModel", lazy="joined")
