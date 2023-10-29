import asyncio

from .bot import Ordis


async def main() -> None:
    bot = Ordis()

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
