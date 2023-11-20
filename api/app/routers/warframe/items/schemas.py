from pydantic import BaseModel


class ItemsSyncResponse(BaseModel):
    response: str


class WarframeItemResponse(BaseModel):
    id: str
    thumb: str
    item_name: str
    url_name: str
