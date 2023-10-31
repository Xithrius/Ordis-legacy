from asyncio import to_thread

from discord.ext.commands import Cog, Context, command
from pydantic import BaseModel
from rapidfuzz import fuzz

from bot.bot import Ordis

BASE_ASSETS_URL = "https://warframe.market/static/assets"


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


class MarketSetItem(BaseModel):
    sub_icon: str
    trading_tax: int
    icon: str
    quantity_for_set: int
    ducats: int
    id: str
    url_name: str
    tags: list[str]
    mastery_level: int
    icon_format: str
    set_root: bool
    thumb: str
    en: MarketSetItemDescription


class MarketSet(BaseModel):
    id: str
    items_in_set: list[MarketSetItem]


class Market(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot
        self.items: list[MarketItem] = []

    async def populate_items_cache(self) -> None:
        r = await self.bot.warframe_market_api.get(
            "/items",
        )

        data = r.json()

        items = data["payload"]["items"]

        self.items = [MarketItem(**item) for item in items]

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

        item_set = MarketSet(**(data["payload"]["item"]))

        return item_set

    @command()
    async def market(self, ctx: Context, *, search: str) -> None:
        if not len(self.items):
            async with ctx.typing():
                await self.populate_items_cache()

        item = await to_thread(self.fuzzy_find_key, search)

        item_set = await self.process_items_in_set(item.url_name)

        await ctx.send(item_set)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Market(bot))
