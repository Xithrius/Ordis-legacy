from discord.ext.commands import Cog, group

from bot.context import Context
from bot.bot import Ordis

class Ping(Cog):
    """Pinging different things."""

    def __init__(self, bot: Ordis):
        self.bot = bot

    @group()
    async def ping(self, ctx: Context) -> None:
        """Is this thing on?"""
        if ctx.invoked_subcommand is None:
            await ctx.send(":ping_pong: Pong!")

    @ping.command()
    async def api(self, ctx: Context) -> None:
        """Is *that* thing on?"""
        j = await self.bot.api.get("/api/ping/")

        await ctx.send(f"API received ping at: {j.data['ping']}")

    @ping.command(aliases=("discord",))
    async def latency(self, ctx: Context) -> None:
        await ctx.send(f"Latency: {self.bot.latency*1000:.0f}ms")


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Ping(bot))
