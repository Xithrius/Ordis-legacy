import os

from discord import AllowedMentions, Intents
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger as log

load_dotenv()


class Ordis(commands.Bot):
    """A subclass where important tasks and connections are created."""

    def __init__(self) -> None:
        """Initializing the bot with proper permissions."""
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=".",
            case_insensitive=True,
            help_command=None,
            allowed_mentions=AllowedMentions(everyone=False),
            intents=intents,
        )

    async def start(self):
        token = os.getenv("BOT_TOKEN")

        if token is None:
            log.error("Retrieving token returned none")
            exit(1)

        await super().start(token=token)

    @staticmethod
    async def on_ready() -> None:
        """Updates the bot status when logged in successfully."""
        log.info("Awaiting...")
