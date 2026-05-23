from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects import postgresql as pg
from sqlmodel import Field, SQLModel


# ===== 게임 기본정보 =====
class Game(SQLModel, table=True):
    __tablename__ = "games"

    app_id: int = Field(primary_key=True)
    name: str
    developer: Optional[str] = None
    publisher: Optional[str] = None
    is_free: bool = False
    is_indie: bool = False
    release_date: Optional[date] = None
    header_image: Optional[str] = None
    metacritic_score: Optional[int] = None
    metacritic_url: Optional[str] = None
    peak_in_game: Optional[int] = Field(sa_column=Column(pg.BIGINT))
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ===== 장르 정규화 =====
class Genre(SQLModel, table=True):
    __tablename__ = "genres"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)


class GameGenre(SQLModel, table=True):
    __tablename__ = "game_genres"

    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("games.app_id", ondelete="CASCADE")))
    genre_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("genres.id", ondelete="CASCADE")))


# ===== 가격 히스토리 =====
class PriceHistory(SQLModel, table=True):
    __tablename__ = "price_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("games.app_id", ondelete="CASCADE")))
    price: Decimal = Field(sa_column=Column(pg.NUMERIC(10, 2)))
    original_price: Decimal = Field(sa_column=Column(pg.NUMERIC(10, 2)))
    discount_rate: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))  # Transform 단계에서 계산
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("idx_price_history_app_collected", "app_id", "collected_at"),)


# ===== 동시접속자 시계열 =====
class PlayerCount(SQLModel, table=True):
    __tablename__ = "player_counts"

    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("games.app_id", ondelete="CASCADE")))
    player_count: int
    collected_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (Index("idx_player_counts_app_collected", "app_id", "collected_at"),)


# ===== 리뷰 스냅샷 (리뷰 폭증 감지용) =====
class ReviewSnapshot(SQLModel, table=True):
    __tablename__ = "reviews_snapshot"

    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("games.app_id", ondelete="CASCADE")))
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    positive_ratio: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))  # Transform 단계에서 계산
    collected_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (Index("idx_reviews_snapshot_app_collected", "app_id", "collected_at"),)


# ===== 리뷰 원문 (NLP 분석용) =====
class ReviewText(SQLModel, table=True):
    __tablename__ = "review_texts"

    review_id: str = Field(primary_key=True)  # Steam 고유 ID (중복 수집 방지)
    app_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("games.app_id", ondelete="CASCADE")))
    review_text: str
    voted_up: bool
    playtime_hours: Optional[int] = None
    language: Optional[str] = None
    created_at: Optional[datetime] = None  # 원본 리뷰 작성 시간
    collected_at: datetime = Field(default_factory=datetime.utcnow)  # ETL 수집 시간


# ===== 리뷰 NLP 분석 결과 (ReviewText와 분리) =====
class ReviewAnalysis(SQLModel, table=True):
    __tablename__ = "review_analysis"

    review_id: str = Field(
        sa_column=Column(pg.TEXT, ForeignKey("review_texts.review_id", ondelete="CASCADE"), primary_key=True)
    )
    sentiment_score: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))
    toxicity: Optional[Decimal] = Field(default=None, sa_column=Column(pg.NUMERIC(5, 4)))
    emotion: Optional[str] = None  # ex) "joy", "anger", "neutral"
    topic: Optional[str] = None  # ex) "gameplay", "graphics", "story"
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# ===== 장르별 집계 (ETL Transform 결과) =====
class GenreStat(SQLModel, table=True):
    __tablename__ = "genre_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    genre_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("genres.id", ondelete="CASCADE")))
    avg_price: Decimal = Field(sa_column=Column(pg.NUMERIC(10, 2)))
    avg_positive_ratio: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))
    total_games: int
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# ===== 숨은 명작 점수 (ETL Transform 결과) =====
class HiddenGem(SQLModel, table=True):
    __tablename__ = "hidden_gems"

    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(sa_column=Column(pg.INTEGER, ForeignKey("games.app_id", ondelete="CASCADE")))
    gem_score: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))
    positive_ratio: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))
    review_count: int
    recent_positive_ratio: Decimal = Field(sa_column=Column(pg.NUMERIC(5, 4)))
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("app_id", "calculated_at"),  # 배치 재실행 중복 방지
    )
