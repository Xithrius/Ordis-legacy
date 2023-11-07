from pydantic import BaseModel


class SyncResponse(BaseModel):
    response: str
