from typing import Any

from pydantic import BaseModel


class MarketUser(BaseModel):
    reputation: int
    locale: str
    avatar: str | None = None
    last_seen: str
    ingame_name: str
    id: str
    region: str
    status: str


class MarketOrderBase(BaseModel):
    quantity: int
    platinum: int
    visible: bool
    order_type: str
    platform: str
    creation_date: str
    last_update: str
    id: str
    region: str


class MarketOrderWithUser(MarketOrderBase):
    user: MarketUser


class MarketOrderWithCombinedUser(MarketOrderBase):
    user_reputation: int
    user_ingame_name: str
    mod_rank: int | None = None


class MarketItem(BaseModel):
    item_name: str
    url_name: str
    thumb: str
    id: str


class MarketSetItemDescription(BaseModel):
    item_name: str
    description: str
    wiki_link: str
    thumb: str
    icon: str
    drop: list


class MarketSetWarframeOrItem(BaseModel):
    sub_icon: str | None = None
    trading_tax: int
    icon: str
    quantity_for_set: int = None
    ducats: int | None = None
    id: str
    url_name: str
    tags: list[str]
    mastery_level: int | None = None
    icon_format: str
    set_root: bool | None = None
    thumb: str
    en: MarketSetItemDescription

    class Config:
        extra = "ignore"


class MarketSetMod(BaseModel):
    sub_icon: str | None = None
    trading_tax: int
    icon: str
    rarity: str
    id: str
    url_name: str
    tags: list[str]
    mod_max_rank: str
    icon_format: str
    thumb: str
    en: Any

    class Config:
        extra = "ignore"

class MarketSet(BaseModel):
    id: str
    items_in_set: list[MarketSetWarframeOrItem | MarketSetMod]
