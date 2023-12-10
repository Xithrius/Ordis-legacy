from dataclasses import dataclass
from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, Context, command

from bot.bot import Ordis
from bot.utils import bold


@dataclass
class EarthState:
    id: str
    expiry: str
    activation: str
    isDay: bool  # noqa: N815
    state: str
    timeLeft: str  # noqa: N815


FROM_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
TO_DATE_FORMAT = "%A, %B %d, %Y %I:%M%p"


class Earth(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot

    @staticmethod
    def convert_datetime_format(datetime_str: str) -> str:
        d = datetime.strptime(datetime_str, FROM_DATE_FORMAT).astimezone()

        return d.strftime(TO_DATE_FORMAT)

    @command(aliases=("earth",))
    async def earth_info(self, ctx: Context) -> None:
        r = await self.bot.warframe_status_api.get(
            "/earthCycle/",
        )

        data = EarthState(**r.json())

        started, ended = (
            self.convert_datetime_format(data.activation),
            self.convert_datetime_format(data.expiry),
        )

        embed = Embed(
            title=f"It is {data.state.capitalize()} for another {data.timeLeft}",
            description=f"Started on {bold(started)}, will end on {bold(ended)}",
        )

        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Earth(bot))
