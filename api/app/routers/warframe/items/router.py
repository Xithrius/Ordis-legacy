from typing import Annotated

from fastapi import APIRouter, Depends, status
from httpx import AsyncClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db_session
from app.database.models.warframe import WarframeMarketOrderModel

from .schemas import SyncResponse

router = APIRouter()

warframe_market_api = AsyncClient(
    base_url="https://api.warframe.market/v1/",
    headers={"Language": "en"},
)


@router.get(
    "/sync",
    response_description="Syncing all items in Warframe with the database",
    response_model=SyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_item(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SyncResponse:
    r = await warframe_market_api.get("/items")

    data = r.json()

    items = data["payload"]["items"]

    result = await session.execute(
        insert(WarframeMarketOrderModel)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(WarframeMarketOrderModel),
        items,
    )

    return SyncResponse(response=f"Populated cache with {len(result)} item(s).")
