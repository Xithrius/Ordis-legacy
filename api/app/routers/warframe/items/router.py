from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db_session
from app.database.models.warframe import WarframeItemModel

from .schemas import ItemsSyncResponse, WarframeItemResponse

router = APIRouter()

warframe_market_api = AsyncClient(
    base_url="https://api.warframe.market/v1/",
    headers={"Language": "en"},
)


@router.get(
    "/sync",
    response_description="Syncing all items in Warframe with the database",
    response_model=ItemsSyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_item(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemsSyncResponse:
    r = await warframe_market_api.get("/items")

    data = r.json()

    items = data["payload"]["items"]

    result = await session.execute(
        insert(WarframeItemModel).on_conflict_do_nothing(index_elements=["id"]).returning(WarframeItemModel),
        items,
    )

    rows = result.all()

    return ItemsSyncResponse(response=f"Populated cache with {len(rows)} item(s).")


@router.get(
    "/all",
    response_description="All the items that currently exist",
    response_model=list[WarframeItemResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_items(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int | None = None,
    offset: int | None = None,
) -> list[WarframeItemModel]:
    stmt = select(WarframeItemModel).limit(limit).offset(offset)

    items = await session.execute(stmt)

    return list(items.scalars().fetchall())


@router.get(
    "/{item_id}",
    response_model=WarframeItemResponse,
    response_description="A specific Warframe item",
    status_code=status.HTTP_200_OK,
)
async def get_trusted_user(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    item_id: str,
) -> WarframeItemModel:
    stmt = select(WarframeItemModel).where({WarframeItemModel.id == item_id})

    items = await session.execute(stmt)

    if (item := items.scalar_one_or_none()) is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Item with ID {item_id} could not be found",
        )

    return item
