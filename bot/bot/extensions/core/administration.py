from discord.ext.commands import Cog, command
from loguru import logger as log

from bot.bot import Ordis
from bot.context import Context
from bot.utils import is_trusted


class Administration(Cog):
    """Admin-specific commands."""

    def __init__(self, bot: Ordis) -> None:
        self.bot = bot

    @command(alias=("logout",))
    @is_trusted()
    async def shutdown(self, ctx: Context) -> None:
        """Shuts the bot down."""
        log.info("Logging out...")

        await ctx.send("Goodbye.")

        await self.bot.close()


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Administration(bot))
