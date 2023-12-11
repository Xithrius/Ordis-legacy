from collections.abc import Awaitable, Callable
from functools import wraps

from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button

from bot.models.warframe_market import MarketOrderWithCombinedUser


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
