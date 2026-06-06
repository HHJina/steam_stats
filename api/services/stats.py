from sqlalchemy import text
from sqlmodel import Session, select

from api.models.game import Game, GameGenre, Genre


class StatsService:
    @staticmethod
    def get_genre_stats(session: Session):
        result = session.execute(
            text("""
            SELECT
                g.name AS genre_name,
                AVG(ph.price) AS avg_price,
                COUNT(DISTINCT gg.app_id) AS total_games
            FROM genres g
            JOIN game_genres gg ON g.id = gg.genre_id
            LEFT JOIN (
                SELECT DISTINCT ON (app_id) app_id, price
                FROM price_history
                ORDER BY app_id, collected_at DESC
            ) ph ON gg.app_id = ph.app_id
            GROUP BY g.name
            ORDER BY total_games DESC
            """)
        )

        return [
            {
                "genre_name": row.genre_name,
                "avg_price": row.avg_price or 0,
                "total_games": row.total_games,
            }
            for row in result.fetchall()
        ]

    @staticmethod
    def get_top_player_games(session: Session, limit: int = 20):
        result = session.execute(
            text("""
            SELECT
                g.app_id,
                g.name,
                g.header_image,
                pc.player_count
            FROM games g
            JOIN (
                SELECT DISTINCT ON (app_id) app_id, player_count
                FROM player_counts
                ORDER BY app_id, collected_at DESC
            ) pc ON g.app_id = pc.app_id
            ORDER BY pc.player_count DESC
            LIMIT :limit
            """),
            {"limit": limit},
        )

        return [
            {
                "app_id": row.app_id,
                "name": row.name,
                "header_image": row.header_image,
                "player_count": row.player_count,
            }
            for row in result.fetchall()
        ]

    @staticmethod
    def get_indie_by_genre(genre_name: str, session: Session, limit: int = 20):
        genre = session.exec(select(Genre).where(Genre.name == genre_name)).first()

        if not genre:
            return []

        return session.exec(
            select(Game)
            .join(GameGenre, Game.app_id == GameGenre.app_id)  # type: ignore[arg-type]
            .where(GameGenre.genre_id == genre.id)
            .where(Game.is_indie)
            .limit(limit)
        ).all()
