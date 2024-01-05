from discord import Embed, Permissions
from discord.ext.commands import Cog, command
from discord.utils import oauth_url

from bot.bot import Ordis
from bot.context import Context
from bot.utils import markdown_link

GITHUB_URL = "https://github.com/Xithrius/Ordis"
BOT_ID_INTEGER = 824131540912177162
PERMISSIONS_INTEGER = 412320386112


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

    @command()
    async def invite(self, ctx: Context) -> None:
        url = oauth_url(BOT_ID_INTEGER, permissions=Permissions(PERMISSIONS_INTEGER))

        embed = Embed(
            description=markdown_link(
                desc="Invite link",
                link=url,
            ),
        )

        await ctx.send(embed=embed)


async def setup(bot: Ordis) -> None:
    await bot.add_cog(Links(bot))
