from os import getenv

from bot.bot import Ordis

bot_instance = Ordis(
    command_prefix="Ordis ",
    help_command=None
)

bot_instance.run(getenv("BOT_TOKEN"), bot=True, reconnect=True)
