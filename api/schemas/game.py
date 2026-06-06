from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class GameResponse(BaseModel):
    app_id: int
    name: str
    developer: str | None
    publisher: str | None
    is_free: bool
    is_indie: bool
    release_date: date | None
    header_image: str | None
    metacritic_score: int | None
    peak_in_game: int | None

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    total: int
    items: list[GameResponse]


class PriceHistoryResponse(BaseModel):
    price: Decimal
    original_price: Decimal
    discount_rate: Decimal
    collected_at: datetime

    class Config:
        from_attributes = True


class PlayerCountResponse(BaseModel):
    player_count: int
    collected_at: datetime

    class Config:
        from_attributes = True
