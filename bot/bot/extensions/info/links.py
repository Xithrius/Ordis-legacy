from discord import Embed, Permissions
from discord.ext.commands import Cog, command
from discord.utils import oauth_url

from bot.bot import Ordis
from bot.context import Context
from bot.utils import markdown_link

GITHUB_URL = "https://github.com/Xithrius/Ordis"

PERMISSIONS_INTEGER = 412317764672

BOT_ID_INTEGER = 591885341812850699


class Links(Cog):
    """Links to many things around the internet, including bot statistics."""

    def __init__(self, bot: Ordis) -> None:
        self.bot = bot

    @command(aliases=("repository", "repo"))
    async def info(self, ctx: Context) -> None:
        """Information about bot origin."""
        embed = Embed(
            description=markdown_link(
                desc="Ordis Github Repository",
                link=GITHUB_URL,
            ),
        )

        await ctx.send(embed=embed)

    @command()
    async def invite(self, ctx: Context) -> None:
        """Provides an invitation link that refers to this bot."""
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
