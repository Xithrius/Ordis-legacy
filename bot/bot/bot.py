from asyncio import Task
from os import getenv

from discord import AllowedMentions, Intents, Message
from discord.ext.commands import Bot, when_mentioned_or
from dotenv import load_dotenv
from loguru import logger as log

from bot import extensions
from bot.api import LocalAPIClient, WarframeMarketAPIClient, WarframeStatusAPIClient
from bot.context import Context
from bot.utils import walk_extensions

load_dotenv()

API_HEALTHCHECK_ATTEMPTS = 5


class Ordis(Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        command_prefix: str = getenv("BOT_PREFIX", ".")

        super().__init__(
            command_prefix=when_mentioned_or(command_prefix),
            case_insensitive=True,
            allowed_mentions=AllowedMentions(everyone=False),
            intents=intents,
        )

        self.database_items_synced: bool = False
        self.database_items_sync_task: Task[None]

    async def get_context(self, message: Message, *, cls: Context = Context) -> Context:  # type: ignore [assignment]
        return await super().get_context(message, cls=cls)

    async def populate_items_cache(self) -> None:
        log.info("Syncing item cache...")

        r = await self.api.get("/api/warframe/items/sync")

        if not r.is_success:
            log.info(f"Item database failed to sync: {r.text}.")

        new = r.json()["new"]

        log.info(f"Item database synced successfully with {new} new item(s).")

        self.database_items_synced = True

    @staticmethod
    async def api_healthcheck(api: LocalAPIClient) -> bool:
        for i in range(API_HEALTHCHECK_ATTEMPTS):
            timeout = (i + 1) * 2
            log.info(f"({i + 1}/10): Attempting to connect to API, timeout of {timeout}...")
            response = await api.get("/api/health", timeout=timeout)

            if response.is_success:
                return True

        return False

    async def setup_hook(self) -> None:
        api_base_url = getenv("API_URL", "http://localhost:8000")

        log.info(f"Attempting to connect to API at {api_base_url}")
        self.api = LocalAPIClient(base_url=api_base_url)
        internal_api_health = await self.api_healthcheck(self.api)
        if not internal_api_health:
            log.critical("Attempted to connect to API, but failed. Exiting...")
            return

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
