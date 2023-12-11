from discord import Embed
from discord.ext.commands import Cog, command

from bot.bot import Ordis
from bot.context import Context
from bot.utils import markdown_link

GITHUB_URL = "https://github.com/Xithrius/Ordis"


class Links(Cog):
    def __init__(self, bot: Ordis) -> None:
        self.bot = bot

    @command(aliases=("repository", "repo"))
    async def info(self, ctx: Context) -> None:
        embed = Embed(
            description=markdown_link(
                desc="Ordis Github Repository",
                link=GITHUB_URL,
            ),
        )

        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Links(bot))
