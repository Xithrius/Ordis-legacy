from pydantic import BaseModel


class ItemsSyncResponse(BaseModel):
    new: int


class WarframeItemResponse(BaseModel):
    id: str
    thumb: str
    item_name: str
    url_name: str
