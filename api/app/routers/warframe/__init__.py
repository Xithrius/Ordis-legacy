from fastapi import APIRouter
from .items import router as items_router
from .order_tracking import router as order_tracking_router

router = APIRouter(prefix="/warframe")

router.include_router(items_router, prefix="/items")
router.include_router(order_tracking_router, prefix="/tracking")

__all__ = ("router",)
