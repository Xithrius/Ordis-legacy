import importlib
import inspect
import pkgutil
from collections.abc import Iterator
from os import getenv
from typing import NoReturn

from discord import AllowedMentions, Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from httpx import AsyncClient
from loguru import logger as log

from . import extensions

load_dotenv()


def walk_extensions() -> Iterator[str]:
    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    for module in pkgutil.walk_packages(
        extensions.__path__,
        f"{extensions.__name__}.",
        onerror=on_error,
    ):
        if module.name.rsplit(".", maxsplit=1)[-1].startswith("_"):
            continue

        if module.ispkg:
            imported = importlib.import_module(module.name)
            if not inspect.isfunction(getattr(imported, "setup", None)):
                continue

        yield module.name


EXTENSIONS = frozenset(walk_extensions())


class Ordis(Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=";;;",
            case_insensitive=True,
            allowed_mentions=AllowedMentions(everyone=False),
            intents=intents,
        )

    async def setup_hook(self) -> None:
        self.warframe_status_api = AsyncClient(
            base_url="https://docs.warframestat.us/pc/",
            params={"language": "en"},
        )
        self.warframe_market_api = AsyncClient(
            base_url="https://api.warframe.market/v1/",
            headers={"Language": "en"},
        )

        for extension in EXTENSIONS:
            await self.load_extension(extension)

            ext_name = ".".join(extension.split(".")[-2:])
            log.info(f'Loading extension "{ext_name}"')

    async def start(self) -> None:
        token = getenv("BOT_TOKEN")

        if token is None:
            log.error("Retrieving token returned none")
            exit(1)

        await super().start(token=token)

    async def close(self) -> None:
        await self.warframe_status_api.aclose()
        await self.warframe_market_api.aclose()

        await super().close()

    @staticmethod
    async def on_ready() -> None:
        log.info("Awaiting...")
