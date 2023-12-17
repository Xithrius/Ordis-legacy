from collections.abc import Callable

from discord.ext.commands import Context, check
from httpx import Response

from bot.bot import Ordis


def is_trusted() -> Callable:
    async def predicate(ctx: Context) -> bool:
        if await ctx.bot.is_owner(ctx.message.author):
            return True

        bot: Ordis = ctx.bot

        response: Response = await bot.api.get(
            f"/trusted/{ctx.message.author.id}",
        )

        return response.is_success

    return check(predicate)
