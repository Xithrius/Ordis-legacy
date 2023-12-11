import pandas as pd
from discord import Embed
from discord.ext.commands import Cog, Context, group
from loguru import logger as log

from bot.bot import Ordis
from bot.models import MarketItem, MarketOrderWithCombinedUser, MarketSet
from bot.utils.plotting import plot_histogram_2d

from ._ui import MarketViewBuyInteraction, MarketViewSellInteraction

BASE_ASSETS_URL = "https://warframe.market/static/assets"


class Market(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot
        self.synced = False

        self.items_sync_task = self.bot.loop.create_task(self.populate_items_cache())

    async def cog_unload(self) -> None:
        self.items_sync_task.cancel()

    async def populate_items_cache(self) -> None:
        await self.bot.wait_until_ready()

        log.info("Syncing item cache...")

        r = await self.bot.api.get("/warframe/items/sync")

        if not r.is_success:
            log.info(f"Item database failed to sync: {r.text}.")

        new = r.json()["new"]

        log.info(f"Item database synced successfully with {new} new item(s).")

        self.synced = True

    async def fuzzy_find_key(self, search: str) -> MarketItem | None:
        r = await self.bot.api.get(f"/warframe/items/find?search={search}")

        if not r.is_success:
            return None

        return MarketItem(**r.json())

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

        item_orders = data["payload"]["orders"]

        return item_orders

    @group()
    async def market(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Missing subcommand")

    @market.command(aliases=("item",))
    async def market_item(self, ctx: Context, *, search: str) -> None:
        if not self.synced:
            await ctx.send("Items database is syncing. Please try again later.")

            return

        if (item := await self.fuzzy_find_key(search.lower())) is None:
            await ctx.send(f"Item '{search}' could not be found.")

            return

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

        if not self.synced:
            await ctx.reply("Items database is syncing. Please try again later.")

            return

        if (item := await self.fuzzy_find_key(search.lower())) is None:
            await ctx.send(f"Item '{search}' could not be found.")

            return

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

    @market.command(aliases=("distro",))
    async def distribution(self, ctx: Context, order_type: str, *, search: str) -> None:
        if order_type not in ("buyers", "sellers"):
            raise ValueError(f"Order type '{order_type}' is not of 'buyers' or 'sellers'.")

        if not self.synced:
            await ctx.reply("Items database is syncing. Please try again later.")

            return

        if (item := await self.fuzzy_find_key(search.lower())) is None:
            await ctx.send(f"Item '{search}' could not be found.")

            return

        item_orders = await self.get_market_order(item.url_name)

        df = pd.DataFrame(item_orders)
        filter_orders = "buy" if order_type == "buyers" else "sell"
        df = df[df["order_type"] == filter_orders]

        await plot_histogram_2d(
            df,
            title=f"Cost distribution of {item.item_name}",
            x_label="platinum",
            ctx=ctx,
        )


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Market(bot))
