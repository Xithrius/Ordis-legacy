from discord.ext.commands import Cog, Context, group

from bot.bot import Ordis


class Ping(Cog):
    def __init__(self, bot: Ordis):
        self.bot = bot

    @group()
    async def ping(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(":ping_pong: Pong!")

    @ping.command(aliases=("discord",))
    async def latency(self, ctx: Context) -> None:
        await ctx.send(f"Latency: {self.bot.latency*1000:.0f}ms")


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Ping(bot))
