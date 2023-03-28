import itertools
import logging
import random

import yaml
from discord import Message
from discord.ext.commands import Bot, Cog

log = logging.getLogger(__name__)


class Ordis(Bot):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_cog(MainCog(self))

    @staticmethod
    async def on_ready() -> None:
        log.trace("Awaiting...")


class MainCog(Cog):

    def __init__(self, bot: Ordis) -> None:
        self.bot = bot

        with open("./ordis/resources/quotes.yaml", mode="r", encoding="utf-8") as f:
            self.all_quotes = yaml.load(f, yaml.FullLoader)

        quote_indexes = list(range(len(self.all_quotes)))
        random.shuffle(quote_indexes)

        self.message_cycle_indexes = itertools.cycle(quote_indexes)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not random.randint(0, 30):
            await message.channel.send(self.all_quotes[next(self.message_cycle_indexes)])
