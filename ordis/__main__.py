import asyncio

from ordis.bot import Ordis


async def main():
    bot = Ordis()
    await bot.start()


asyncio.run(main())
