import importlib
import inspect
import pkgutil
import sys
import traceback
import types
from asyncio import Task
from collections.abc import Iterator
from os import getenv
from typing import NoReturn

from discord import AllowedMentions, Embed, Intents, Interaction, Message, app_commands
from discord.ext.commands import Bot, CommandError, when_mentioned_or
from dotenv import load_dotenv
from loguru import logger as log

from bot import extensions
from bot.api import LocalAPIClient, WarframeMarketAPIClient, WarframeStatusAPIClient
from bot.context import Context

load_dotenv()


def ignore_module(module: pkgutil.ModuleInfo) -> bool:
    return any(name.startswith("_") for name in module.name.split("."))


def walk_extensions(module: types.ModuleType) -> Iterator[str]:
    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    modules = set()

    for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}.", onerror=on_error):
        if ignore_module(module_info):
            continue

        if module_info.ispkg:
            imported = importlib.import_module(module_info.name)
            if not inspect.isfunction(getattr(imported, "setup", None)):
                continue

        modules.add(module_info.name)

    return frozenset(modules)


class Ordis(Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=when_mentioned_or(";"),
            case_insensitive=True,
            allowed_mentions=AllowedMentions(everyone=False),
            intents=intents,
        )

        self.database_items_synced: bool = False
        self.database_items_sync_task: Task | None = None

    async def get_context(self, message: Message, *, cls: Context = Context) -> Context:
        """Defines the custom context."""
        return await super().get_context(message, cls=cls)

    async def populate_items_cache(self) -> None:
        log.info("Syncing item cache...")

        r = await self.api.get("/warframe/items/sync")

        if not r.is_success:
            log.info(f"Item database failed to sync: {r.text}.")

        new = r.json()["new"]

        log.info(f"Item database synced successfully with {new} new item(s).")

        self.database_items_synced = True

    async def setup_hook(self) -> None:
        self.api = LocalAPIClient(
            base_url=getenv("API_URL", "http://localhost:8000/api/"),
        )
        self.warframe_status_api = WarframeStatusAPIClient(
            base_url="https://api.warframestat.us/pc/",
            params={"language": "en"},
        )
        self.warframe_market_api = WarframeMarketAPIClient(
            base_url="https://api.warframe.market/v1/",
            headers={"Language": "en"},
        )

        self.database_items_sync_task = self.loop.create_task(self.populate_items_cache())

        exts = walk_extensions(extensions)

        for extension in exts:
            await self.load_extension(extension)

            ext_name = ".".join(extension.split(".")[-2:])
            log.info(f'Loading extension "{ext_name}"')

    async def on_command_error(
        self,
        ctx: Context | Interaction,
        error: CommandError | app_commands.AppCommandError,
    ) -> None:
        if isinstance(ctx, Interaction) or ctx.command is None:
            return

        log.error(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)

        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
            file=sys.stderr,
        )

        embed = Embed(description=f"```{error}```")

        await ctx.send(embed=embed)

    async def start(self) -> None:
        token = getenv("BOT_TOKEN")

        if token is None:
            log.error("Retrieving token returned none")
            exit(1)

        await super().start(token=token)

    async def close(self) -> None:
        self.database_items_sync_task.cancel()

        await self.warframe_status_api.aclose()
        await self.warframe_market_api.aclose()

        await super().close()

    @staticmethod
    async def on_ready() -> None:
        log.info("Awaiting...")
