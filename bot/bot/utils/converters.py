from discord.ext.commands import Context, Converter

from bot.bot import EXTENSIONS


class Extension(Converter):
    async def convert(self, ctx: Context, argument: str) -> str:
        argument = argument.lower()

        if "." not in argument:
            argument = f"bot.extensions.{argument}"

        if argument in EXTENSIONS:
            return argument

        raise ValueError(f"Invalid argument {argument}")
