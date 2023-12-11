import importlib
import inspect
import pkgutil
import sys
import traceback
import types
from collections.abc import Iterator
from os import getenv
from typing import NoReturn

from discord import AllowedMentions, Embed, Intents, Interaction, Message, app_commands
from discord.ext.commands import Bot, CommandError
from dotenv import load_dotenv
from httpx import AsyncClient
from loguru import logger as log

from bot import extensions
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
            command_prefix=";;;",
            case_insensitive=True,
            allowed_mentions=AllowedMentions(everyone=False),
            intents=intents,
        )

    async def get_context(self, message: Message, *, cls: Context = Context) -> Context:
        """Defines the custom context."""
        return await super().get_context(message, cls=cls)

    async def setup_hook(self) -> None:
        self.api = AsyncClient(
            base_url=getenv("API_URL", "http://localhost:8000/api/"),
        )

        self.warframe_status_api = AsyncClient(
            base_url="https://api.warframestat.us/pc/",
            params={"language": "en"},
        )
        self.warframe_market_api = AsyncClient(
            base_url="https://api.warframe.market/v1/",
            headers={"Language": "en"},
        )

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
        await self.warframe_status_api.aclose()
        await self.warframe_market_api.aclose()

        await super().close()

    @staticmethod
    async def on_ready() -> None:
        log.info("Awaiting...")
