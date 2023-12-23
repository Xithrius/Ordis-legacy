from collections.abc import Awaitable, Callable
from functools import wraps

import pandas as pd
from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button

from bot.models import MarketOrderWithCombinedUser
from bot.utils import barplot_2d, histogram_2d


class MarketView(View):
    def __init__(
        self,
        df: pd.DataFrame,
        url_name: str,
        name: str,
        item: MarketOrderWithCombinedUser,
    ) -> None:
        super().__init__()

        self.df = df
        self.url = url_name
        self.name = name
        self.item = item

        self.add_item(
            Button(
                label="warframe.market",
                url=f"https://warframe.market/items/{url_name}",
            ),
        )

    @button(label="Cost distribution", style=ButtonStyle.blurple)
    async def cost_distribution(self, interaction: Interaction, button: Button) -> None:
        await histogram_2d(
            self.df,
            title=f"Cost distribution of {self.name}",
            x_label="platinum",
            ctx=interaction,
        )

    @button(label="Percentiles", style=ButtonStyle.blurple)
    async def percentiles(self, interaction: Interaction, button: Button) -> None:
        s = self.df["platinum"]

        stats_df = pd.DataFrame(
            {
                "percentiles": [
                    "Min",
                    "Mean",
                    "Median",
                    "0.95",
                    "0.99",
                    "0.999",
                    "Max",
                ],
                "platinum": [
                    s.min(),
                    s.mean(),
                    s.median(),
                    s.quantile(0.95),
                    s.quantile(0.99),
                    s.quantile(0.999),
                    s.max(),
                ],
            },
        )

        await barplot_2d(
            stats_df,
            title=f"Percentiles of {self.name}",
            x_label="percentiles",
            y_label="platinum",
            include_outliers=True,
            ctx=interaction,
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
