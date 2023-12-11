from discord.ext.commands import Cog, command
from loguru import logger as log

from bot.bot import Ordis
from bot.context import Context


class Administration(Cog):
    def __init__(self, bot: Ordis) -> None:
        self.bot = bot

    @command(alias=("logout",))
    async def shutdown(self, ctx: Context) -> None:
        log.info("Logging out...")

        await ctx.send("Goodbye.")

        await self.bot.close()


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Administration(bot))
