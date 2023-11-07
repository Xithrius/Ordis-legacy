from asyncio import to_thread
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

import pandas as pd
from discord import ButtonStyle, Embed, Interaction
from discord.ext.commands import Cog, Context, group
from discord.ui import Button, View, button
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


class MarketView(View):
    def __init__(self, url_name: str, name: str, item: MarketOrderWithCombinedUser) -> None:
        super().__init__()

        self.url = url_name
        self.name = name
        self.item = item

        self.add_item(
            Button(
                label="View on warframe.market",
                url=f"https://warframe.market/items/{url_name}",
            ),
        )


def order_interaction(action: str) -> Callable[[], Awaitable[None]]:
    def decorator(func: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        @wraps(func)
        async def wrapper(self: MarketView, interaction: Interaction, button: Button) -> None:
            rank = ""
            if (rank_level := self.item.mod_rank) is not None:
                rank = f" (rank {rank_level})"

            msg = (
                f'/w {self.item.user_ingame_name} Hi! I want to {action}: "{self.name}{rank}" '
                f"for {self.item.platinum} platinum. (warframe.market)"
            )

            await interaction.response.send_message(f"```{msg}```", ephemeral=True)
            self.stop()

        return wrapper

    return decorator


class MarketViewBuyInteraction(MarketView):
    @button(label="Buy", style=ButtonStyle.green)
    @order_interaction(action="buy")
    async def buy(self, interaction: Interaction, button: Button) -> None:
        pass


class MarketViewSellInteraction(MarketView):
    @button(label="Sell", style=ButtonStyle.green)
    @order_interaction(action="sell")
    async def sell(self, interaction: Interaction, button: Button) -> None:
        pass


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

    @market.command(aliases=("order",))
    async def market_order(self, ctx: Context, order_type: str, *, search: str) -> None:
        def __build_embed_section(item: MarketOrderWithCombinedUser) -> str:
            ign, rep, quantity, platinum = item.user_ingame_name, item.user_reputation, item.quantity, item.platinum
            action = "buying" if order_type == "buyers" else "selling"

            return f"{ign} (+{rep}) is {action} **{quantity}** for **{platinum}** platinum"

        if order_type not in ("buyers", "sellers"):
            raise ValueError(f"Order type '{order_type}' is not of 'buyers' or 'sellers'.")

        if not len(self.items):
            async with ctx.typing():
                await self.populate_items_cache()

        item = await to_thread(self.fuzzy_find_key, search)

        item_orders = await self.get_market_order(item.url_name)

        df = pd.DataFrame(item_orders)
        filter_orders = "buy" if order_type == "buyers" else "sell"
        df = df[df["order_type"] == filter_orders]

        df["user_reputation"] = df["user"].apply(lambda x: x["reputation"])
        df["user_ingame_name"] = df["user"].apply(lambda x: x["ingame_name"])

        filtered_item = MarketOrderWithCombinedUser(
            **df.sort_values(by=["platinum", "user_reputation"], ascending=[True, True]).iloc[0].to_dict(),
        )

        raw_embed = __build_embed_section(filtered_item)

        item_name = " ".join(f"{x[0].upper()}{x[1:]}" for x in item.item_name.split("_"))

        embed = Embed(title=item_name, description=raw_embed)

        embed.set_thumbnail(url=f"{BASE_ASSETS_URL}/{item.thumb}")

        market_interaction = (
            MarketViewBuyInteraction if filtered_item.order_type == "sell" else MarketViewSellInteraction
        )
        view = market_interaction(item.url_name, item_name, filtered_item)

        await ctx.send(embed=embed, view=view)
        await view.wait()


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Market(bot))
