from discord.ext.commands import Cog, Context, command

from bot.bot import Ordis


class Earth(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot

    @command()
    async def earth_info(self, ctx: Context) -> None:
        r = await self.bot.warframe_status_api.get(
            "/earthCycle",
        )

        data = r.json()

        await ctx.send(data)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Earth(bot))
