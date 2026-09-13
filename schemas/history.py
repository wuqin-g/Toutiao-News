from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id:int=Field(...,alias="newsId")

class HistoryNewsItemResponse(NewsItemBase):
    viewTime:datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class HistoryListResponse(BaseModel):
    list:list[HistoryNewsItemResponse]
    total:int
    hasMore:bool
    model_config = ConfigDict(
        from_attributes=True
    )
