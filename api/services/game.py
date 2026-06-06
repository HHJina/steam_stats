from sqlalchemy import asc
from sqlmodel import Session, select

from api.models.game import Game, GameGenre, Genre, PlayerCount, PriceHistory


class GameService:
    @staticmethod
    def get_games(session: Session, limit: int = 20, offset: int = 0):
        return session.exec(select(Game).limit(limit).offset(offset)).all()

    @staticmethod
    def get_game(app_id: int, session: Session):
        return session.get(Game, app_id)

    @staticmethod
    def get_price_history(app_id: int, session: Session):
        return session.exec(
            select(PriceHistory).where(PriceHistory.app_id == app_id).order_by(asc(PriceHistory.collected_at))  # type: ignore[arg-type]
        ).all()

    @staticmethod
    def get_lowest_price(app_id: int, session: Session):
        result = session.exec(
            select(PriceHistory).where(PriceHistory.app_id == app_id).order_by(asc(PriceHistory.price)).limit(1)  # type: ignore[arg-type]
        ).first()

        if not result:
            return None

        return {
            "lowest_price": result.price,
            "collected_at": result.collected_at,
        }

    @staticmethod
    def get_player_counts(app_id: int, session: Session):
        return session.exec(
            select(PlayerCount).where(PlayerCount.app_id == app_id).order_by(asc(PlayerCount.collected_at))  # type: ignore[arg-type]
        ).all()

    @staticmethod
    def get_games_by_genre(genre_name: str, limit: int, session: Session):
        genre = session.exec(select(Genre).where(Genre.name == genre_name)).first()

        if not genre:
            return []

        return session.exec(
            select(Game)
            .join(GameGenre, Game.app_id == GameGenre.app_id)  # type: ignore[arg-type]
            .where(GameGenre.genre_id == genre.id)
            .limit(limit)
        ).all()

    @staticmethod
    def get_indie_games(limit: int, session: Session):
        return session.exec(select(Game).where(Game.is_indie).limit(limit)).all()
