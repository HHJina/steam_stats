from decimal import Decimal

from pydantic import BaseModel


class GenreStatResponse(BaseModel):
    genre_name: str
    avg_price: Decimal
    total_games: int


class TopPlayerGameResponse(BaseModel):
    app_id: int
    name: str
    header_image: str | None
    player_count: int


class IndieGameResponse(BaseModel):
    app_id: int
    name: str
    header_image: str | None
    is_free: bool
    metacritic_score: int | None

    class Config:
        from_attributes = True
