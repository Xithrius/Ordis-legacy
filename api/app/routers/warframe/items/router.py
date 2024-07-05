from fastapi import APIRouter, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert

from app.database.dependencies import DBSession
from app.database.models.warframe import WarframeItemModel

from .schemas import ItemsSyncResponse, WarframeItemResponse

router = APIRouter()

warframe_market_api = AsyncClient(
    base_url="https://api.warframe.market/v1/",
    headers={"Language": "en"},
    timeout=15.0,
)


@router.get(
    "/sync",
    description="Syncing all items in Warframe with the database",
    response_model=ItemsSyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_items(
    session: DBSession,
) -> ItemsSyncResponse:
    r = await warframe_market_api.get("/items")

    data = r.json()

    items = data["payload"]["items"]

    result = await session.execute(
        insert(WarframeItemModel).on_conflict_do_nothing(index_elements=["id"]).returning(WarframeItemModel),
        items,
    )

    rows = result.all()

    return ItemsSyncResponse(new=len(rows))


@router.get(
    "/all",
    description="All the items that currently exist",
    response_model=list[WarframeItemResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_items(
    session: DBSession,
    limit: int | None = None,
    offset: int | None = None,
) -> list[WarframeItemModel]:
    stmt = select(WarframeItemModel).limit(limit).offset(offset)

    items = await session.execute(stmt)

    return list(items.scalars().fetchall())


@router.get(
    "/find",
    description="Fuzzy find an item by name",
    response_model=WarframeItemResponse,
    status_code=status.HTTP_200_OK,
)
async def get_item_by_fuzzy(
    session: DBSession,
    search: str,
    threshold: float | None = 0.7,
) -> WarframeItemModel:
    stmt = select(WarframeItemModel).where(
        or_(
            func.similarity(WarframeItemModel.item_name, search) > threshold,
            func.similarity(WarframeItemModel.url_name, search) > threshold,
        ),
    )

    items = await session.execute(stmt)

    if (item := items.scalar_one_or_none()) is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Item {search} could not be found",
        )

    return item


@router.get(
    "/{item_id}",
    description="Get a specific warframe item",
    response_model=WarframeItemResponse,
    status_code=status.HTTP_200_OK,
)
async def get_item(
    session: DBSession,
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
