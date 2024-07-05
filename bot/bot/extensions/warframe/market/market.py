import pandas as pd
from discord import Embed
from discord.ext.commands import Cog, group

from bot.bot import Ordis
from bot.context import Context
from bot.models import MarketOrderWithCombinedUser
from bot.utils import barplot_2d

from ._ui import MarketViewBuyInteraction, MarketViewSellInteraction

BASE_ASSETS_URL = "https://warframe.market/static/assets"


class Market(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot

    @group()
    async def market(self, ctx: Context) -> None:
        await ctx.check_subcommands()

    @market.command(aliases=("order",))
    async def market_order(self, ctx: Context, order_type: str, *, search: str) -> None:
        def __build_embed_section(item: MarketOrderWithCombinedUser) -> str:
            ign, rep, quantity, platinum = item.user_ingame_name, item.user_reputation, item.quantity, item.platinum
            action = "buying" if order_type == "buyers" else "selling"

            return f"{ign} (+{rep}) is {action} **{quantity}** for **{platinum}** platinum"

        async def __filter_best_item() -> tuple[MarketOrderWithCombinedUser, pd.DataFrame]:
            if (some_item := item) is not None:
                item_orders = await self.bot.warframe_market_api.get_market_item_orders(some_item.url_name)

            df = pd.DataFrame(item_orders)
            filter_orders = "buy" if order_type == "buyers" else "sell"
            df = df[df["order_type"] == filter_orders]

            df["user_reputation"] = df["user"].apply(lambda x: x["reputation"])
            df["user_ingame_name"] = df["user"].apply(lambda x: x["ingame_name"])

            filtered_item = MarketOrderWithCombinedUser(
                **df.sort_values(by=["platinum", "user_reputation"], ascending=[True, True]).iloc[0].to_dict(),
            )

            return filtered_item, df

        await ctx.typing()

        if order_type not in ("buyers", "sellers"):
            raise ValueError(f"Order type '{order_type}' is not of 'buyers' or 'sellers'.")

        if not self.bot.database_items_synced:
            await ctx.reply("Items database is syncing. Please try again later.")

            return

        if (item := await self.bot.api.fuzzy_find_item(search.lower())) is None:
            await ctx.send(f"Item '{search}' could not be found.")

            return

        best_item, df = await __filter_best_item()

        best_item_obj: MarketOrderWithCombinedUser = best_item

        raw_embed = __build_embed_section(best_item_obj)

        item_name = " ".join(f"{x[0].upper()}{x[1:]}" for x in item.item_name.split("_"))

        embed = Embed(title=item_name, description=raw_embed)

        embed.set_thumbnail(url=f"{BASE_ASSETS_URL}/{item.thumb}")

        market_interaction = MarketViewBuyInteraction if best_item.order_type == "sell" else MarketViewSellInteraction
        view = market_interaction(df, item.url_name, item_name, best_item)

        await ctx.send(embed=embed, view=view)
        await view.wait()

    @market.command(aliases=("distro",))
    async def distribution(self, ctx: Context, order_type: str, *, search: str) -> None:
        if order_type not in ("buyers", "sellers"):
            raise ValueError(f"Order type '{order_type}' is not of 'buyers' or 'sellers'.")

        if not self.bot.database_items_synced:
            await ctx.reply("Items database is syncing. Please try again later.")

            return

        if (item := await self.bot.api.fuzzy_find_item(search.lower())) is None:
            await ctx.send(f"Item '{search}' could not be found.")

            return

        item_orders = await self.bot.warframe_market_api.get_market_item_orders(item.url_name)

        df = pd.DataFrame(item_orders)
        filter_orders = "buy" if order_type == "buyers" else "sell"
        df = df[df["order_type"] == filter_orders]

        await barplot_2d(
            df,
            title=f"Cost distribution of {item.item_name}",
            x_label="platinum",
            y_label="quantity",
            ctx=ctx,
        )


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Market(bot))
