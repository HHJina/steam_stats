from sqlalchemy import text
from sqlmodel import Session


class GemService:
    @staticmethod
    def get_hidden_gems(session: Session, limit: int = 20, offset: int = 0):
        result = session.execute(
            text("""
                SELECT
                    hg.app_id,
                    g.name,
                    g.header_image,
                    hg.gem_score,
                    hg.positive_ratio,
                    hg.review_count,
                    hg.recent_positive_ratio,
                    hg.calculated_at
                FROM hidden_gems hg
                JOIN games g ON hg.app_id = g.app_id
                WHERE hg.calculated_at = (
                    SELECT MAX(calculated_at) FROM hidden_gems
                )
                ORDER BY hg.gem_score DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset},
        )

        return [
            {
                "app_id": row.app_id,
                "name": row.name,
                "header_image": row.header_image,
                "gem_score": row.gem_score,
                "positive_ratio": row.positive_ratio,
                "review_count": row.review_count,
                "recent_positive_ratio": row.recent_positive_ratio,
                "calculated_at": row.calculated_at,
            }
            for row in result.fetchall()
        ]

    @staticmethod
    def get_gem(app_id: int, session: Session):
        result = session.execute(
            text("""
                SELECT
                    hg.app_id,
                    g.name,
                    g.header_image,
                    hg.gem_score,
                    hg.positive_ratio,
                    hg.review_count,
                    hg.recent_positive_ratio,
                    hg.calculated_at
                FROM hidden_gems hg
                JOIN games g ON hg.app_id = g.app_id
                WHERE hg.app_id = :app_id
                ORDER BY hg.calculated_at DESC
                LIMIT 1
            """),
            {"app_id": app_id},
        )

        row = result.fetchone()
        if not row:
            return None

        return {
            "app_id": row.app_id,
            "name": row.name,
            "header_image": row.header_image,
            "gem_score": row.gem_score,
            "positive_ratio": row.positive_ratio,
            "review_count": row.review_count,
            "recent_positive_ratio": row.recent_positive_ratio,
            "calculated_at": row.calculated_at,
        }
