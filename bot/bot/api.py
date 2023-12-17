from httpx import AsyncClient

from bot.models.warframe_market import MarketItem


class LocalAPIClient(AsyncClient):
    async def fuzzy_find_item(self, search: str) -> MarketItem | None:
        r = await self.get(f"/warframe/items/find?search={search}")

        if not r.is_success:
            return None

        return MarketItem(**r.json())


class WarframeStatusAPIClient(AsyncClient):
    ...


class WarframeMarketAPIClient(AsyncClient):
    async def get_market_item_orders(self, item_url: str) -> list[dict]:
        r = await self.get(f"/items/{item_url}/orders")

        data = r.json()

        item_orders = data["payload"]["orders"]

        return item_orders
