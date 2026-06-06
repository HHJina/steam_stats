from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class HiddenGemResponse(BaseModel):
    app_id: int
    name: str
    header_image: str | None
    gem_score: Decimal
    positive_ratio: Decimal
    review_count: int
    recent_positive_ratio: Decimal
    calculated_at: datetime

    class Config:
        from_attributes = True