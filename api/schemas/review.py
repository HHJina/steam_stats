from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ReviewResponse(BaseModel):
    review_id: str
    app_id: int
    review_text: str
    voted_up: bool
    playtime_hours: int | None
    language: str | None
    created_at: datetime | None

    class Config:
        from_attributes = True


class ReviewSnapshotResponse(BaseModel):
    app_id: int
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    positive_ratio: Decimal
    collected_at: datetime

    class Config:
        from_attributes = True


class ReviewSpikeResponse(BaseModel):
    collected_at: datetime
    total_reviews: int
    review_delta: int  # 전날 대비 증가량
    is_positive_spike: bool  # 긍정 폭증 여부
    is_negative_spike: bool  # 부정 폭증 여부
