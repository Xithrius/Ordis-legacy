from asyncio import to_thread
from typing import Any

import pandas as pd
from discord import Embed
from discord.ext.commands import Cog, Context, group
from loguru import logger as log
from pydantic import BaseModel
from rapidfuzz import fuzz

from bot.bot import Ordis

BASE_ASSETS_URL = "https://warframe.market/static/assets"


class MarketUser(BaseModel):
    reputation: int
    locale: str
    avatar: str | None = None
    last_seen: str
    ingame_name: str
    id: str
    region: str
    status: str


class MarketOrder(BaseModel):
    quantity: int
    platinum: int
    visible: bool
    order_type: str
    user: MarketUser
    platform: str
    creation_date: str
    last_update: str
    id: str
    region: str


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


class Market(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot
        self.items: list[MarketItem] = []

    async def populate_items_cache(self) -> None:
        log.info("Item cache is empty. Populating...")

        r = await self.bot.warframe_market_api.get(
            "/items",
        )

        data = r.json()

        items = data["payload"]["items"]

        self.items = [MarketItem(**item) for item in items]

        log.info(f"Item cache populated with {len(self.items)} item(s).")

    def fuzzy_find_key(self, search: str) -> MarketItem:
        best_match: MarketItem | None = None
        best_score = 0

        for item in self.items:
            similarity_score = fuzz.WRatio(search, item.item_name)

            if similarity_score > best_score:
                best_score = similarity_score
                best_match = item

                if similarity_score == 100.0:
                    break

        return best_match

    async def process_items_in_set(self, item_url: str) -> MarketSet:
        r = await self.bot.warframe_market_api.get(
            f"/items/{item_url}",
        )

        data = r.json()

        item_set = MarketSet(**data["payload"]["item"])

        return item_set

    async def get_market_order(self, item_url: str) -> list[dict]:
        r = await self.bot.warframe_market_api.get(
            f"/items/{item_url}/orders",
        )

        data = r.json()

        # item_orders = [MarketOrder(**x) for x in data["payload"]["orders"]]
        item_orders = data["payload"]["orders"]

        return item_orders

    @group()
    async def market(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Missing subcommand")

    @market.command(aliases=("item",))
    async def market_item(self, ctx: Context, *, search: str) -> None:
        if not len(self.items):
            async with ctx.typing():
                await self.populate_items_cache()

        item = await to_thread(self.fuzzy_find_key, search)

        item_set = await self.process_items_in_set(item.url_name)

        await ctx.send(item_set.id)

        # for market_item in item_set.items_in_set:
        #     log.info(f"trading tax: {market_item.trading_tax}")
        # for market_item in [item_set.items_in_set[0]]:
        #     embed = Embed(description=f"trading tax: {market_item.trading_tax}")
        #     embed.set_image(url=f"{BASE_ASSETS_URL}/{market_item.icon}")

        #     await ctx.send(embed=embed)

    @market.command(aliases=("order", "buy", "sell"))
    async def market_order(self, ctx: Context, *, search: str) -> None:
        def __build_embed_section(title: str, sorted_df: pd.DataFrame) -> (str, str):
            bold_title = f"**{title}**"
            user_ingame_name = sorted_df["user_ingame_name"]
            quantity = sorted_df["quantity"]
            platinum = sorted_df["platinum"]

            return f"{bold_title}", f"{quantity} for {platinum} platinum by {user_ingame_name}"

        if not len(self.items):
            async with ctx.typing():
                await self.populate_items_cache()

        item = await to_thread(self.fuzzy_find_key, search)

        item_orders = await self.get_market_order(item.url_name)

        df = pd.DataFrame(item_orders)

        df["user_reputation"] = df["user"].apply(lambda x: x["reputation"])
        df["user_ingame_name"] = df["user"].apply(lambda x: x["ingame_name"])

        sorted_dfs = [
            [
                "Cheapest",
                df.sort_values(by=["platinum", "user_reputation"], ascending=[True, True]).iloc[0],
            ],
            [
                "Highest reputation",
                df.sort_values(by=["platinum", "user_reputation"], ascending=[True, False]).iloc[0],
            ],
        ]

        raw_embeds = [__build_embed_section(x[0], x[1]) for x in sorted_dfs]

        if raw_embeds[0][1] == raw_embeds[1][1]:
            raw_embeds = [("**Cheapest, highest reputation**", raw_embeds[0][1])]

        raw_embed = "\n\n".join(f"{x[0]}\n{x[1]}" for x in raw_embeds)

        item_name = " ".join(f"{x[0].upper()}{x[1:]}" for x in item.item_name.split("_"))

        embed = Embed(title=item_name, description=raw_embed)

        embed.set_thumbnail(url=f"{BASE_ASSETS_URL}/{item.thumb}")

        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Market(bot))
