from dataclasses import dataclass
from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, Context, command

from bot.bot import Ordis


@dataclass
class EarthState:
    id: str
    expiry: datetime
    activation: datetime
    isDay: bool  # noqa: N815
    state: str
    timeLeft: str  # noqa: N815


class Earth(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot

    @command(aliases=("earth",))
    async def earth_info(self, ctx: Context) -> None:
        r = await self.bot.warframe_status_api.get(
            "/earthCycle/",
        )

        data = EarthState(**r.json())

        embed = Embed(
            title=f"It is {data.state.capitalize()} for another {data.timeLeft}",
            description=f"Started at {data.activation}, will end at {data.expiry}",
        )

        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Earth(bot))
