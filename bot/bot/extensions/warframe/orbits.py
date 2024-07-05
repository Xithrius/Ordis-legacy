from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, command

from bot.bot import Ordis
from bot.context import Context
from bot.utils import bold, final_join

FROM_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
TO_DATE_FORMAT = "%A, %B %d, %Y %I:%M%p"

PLANETS = ["earth", "vallis", "cambion", "cetus"]


class Orbits(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot

    @staticmethod
    def convert_datetime_format(datetime_str: str) -> str:
        d = datetime.strptime(datetime_str, FROM_DATE_FORMAT).astimezone()

        return d.strftime(TO_DATE_FORMAT)

    @command(aliases=("orbits",))
    async def orbit(self, ctx: Context, planet: str) -> None:
        if planet not in PLANETS:
            raise ValueError(f"Planet '{planet}' is not of {final_join(PLANETS, final_sep="or")}.")

        r = await self.bot.warframe_status_api.get(f"/{planet}Cycle/")

        data = r.json()

        state, time_left, activation, expiry = (
            data["state"].capitalize(),
            data["timeLeft"],
            data["activation"],
            data["expiry"],
        )

        started, ended = (
            self.convert_datetime_format(activation),
            self.convert_datetime_format(expiry),
        )

        embed = Embed(
            title=f"It is {state} for another {time_left}",
            description=f"Started on {bold(started)}, will end on {bold(ended)}",
        )

        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Orbits(bot))
