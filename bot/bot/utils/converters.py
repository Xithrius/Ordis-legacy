from discord.ext.commands import Context, Converter

from bot import extensions
from bot.bot import walk_extensions


class Extension(Converter):
    async def convert(self, ctx: Context, argument: str) -> str:
        argument = argument.lower()

        if "." not in argument:
            argument = f"bot.extensions.{argument}"

        exts = walk_extensions(extensions)

        if argument in exts:
            return argument

        raise ValueError(f"Invalid argument {argument}")
