import sys
import traceback

from discord import Embed
from discord.ext.commands import Cog, errors
from loguru import logger as log

from bot.bot import Ordis
from bot.constants import Colours
from bot.context import Context
from bot.utils.checks import TrustedUserCheckFailure


class CommandErrorHandler(Cog):
    """Handling command errors."""

    def __init__(self, bot: Ordis) -> None:
        self.bot = bot

    @staticmethod
    def error_embed(message: str, title: str = "Something bad happened") -> Embed:
        return Embed(title=title, description=message, colour=Colours.soft_red)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, e: errors.CommandError) -> None:
        if isinstance(e, errors.CommandNotFound):
            embed = self.error_embed("That command does not exist")
            await ctx.send(embed=embed)
            return
        if isinstance(e, TrustedUserCheckFailure):
            embed = self.error_embed("You do not have sufficient trust to run this command")
            await ctx.send(embed=embed)
            return

        log.error("Ignoring exception in command")
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

        embed = self.error_embed(str(e))
        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(CommandErrorHandler(bot))
